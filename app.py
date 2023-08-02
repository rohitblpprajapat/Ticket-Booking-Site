from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, make_response
from werkzeug.utils import secure_filename
from model import *
from sqlalchemy import or_
from datetime import datetime
import os



app = Flask(__name__)
app.secret_key = 'Jai_Shree_Krishna'    
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ticketbooking.sqlite'  


 


# home page

@app.route('/')
def index():
    # Get all venues and their upcoming shows
    venues = Venue.query.all()

            
    return render_template('index.html', venues= venues)


# user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match. Please try again.')
            return redirect(url_for('register'))

        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with that email address already exists. Please log in or use a different email address.')
            return redirect(url_for('register'))

        # Create a new user object and add it to the database
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Your account has been created. Please log in to continue.')
        return redirect(url_for('login'))

    return render_template('register.html')


# user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the email and password match a user in the database
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['user_id'] = user.id
            session['logged_in_u'] = True
            flash('You have been logged in.')
            return redirect(url_for('index'))
        

        flash('Invalid email or password. Please try again.')
        return redirect(url_for('login'))

    return render_template('login.html')

# user logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session['logged_in'] = False
    flash('You have been logged out.')
    return redirect(url_for('login'))

# User dashboard route
@app.route('/dashboard/<int:user_id>')
def user_dashboard(user_id):
    # Check if user is authenticated
    if not session.get('user_id'):
        return redirect(url_for('login'))

    # Get the user object from the database
    user = User.query.filter_by(id=session['user_id']).first()

    # Get all tickets associated with the current user, ordered by show start time
    tickets = Ticket.query.filter_by(user_id=user_id).all() 

    # Render the user dashboard template
    return render_template('user_dashboard.html', user=user, tickets=tickets)



@app.route('/book_tickets/<int:show_id>', methods=['GET', 'POST'])
def book_tickets(show_id):
    show = Show.query.get(show_id)
    if request.method == 'POST':
        num_tickets = request.form.get('num_tickets')
        email = request.form.get('email')

        
        # Get user ID from the current session or user object if logged in
        user = User.query.filter_by(email=email).first()
        if not user:
            return redirect(url_for('login'))
        user_id = user.id
        
        tickets = Ticket(user_id=user_id, show_id=show_id, quantity=num_tickets)
        db.session.add(tickets)
        db.session.commit()
        flash('Tickets booked successfully')
        return redirect(url_for('index'))
    else:
        return render_template('book_tickets.html', show=show)


# Admin login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        # Get the email and password from the form
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the admin exists in the database
        admin = Admin.query.filter_by(email=email).first()

        # If the admin exists and the password is correct, log them in and redirect to the admin dashboard
        if admin and admin.password == password:
            session['admin_id'] = admin.id
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))

        # If the admin does not exist or the password is incorrect, show an error message
        error = 'Invalid email or password'
        return render_template('admin_login.html', error=error)

    # If the request method is GET, render the admin login page
    return render_template('admin_login.html')

# Admin dashboard route

@app.route('/admin/dashboard')
def admin_dashboard():
    # Check if user is authenticated
    if not session.get('admin_id'):
        return redirect(url_for('admin_login'))

    # Get the admin object from the database
    admin = Admin.query.filter_by(id=session['admin_id']).first()
    venues = Venue.query.all()
    shows = Show.query.all()
    

    # Render the admin dashboard template 
    return render_template('admin_dashboard.html', admin=admin, venues=venues, shows=shows )



    
@app.route('/movies')
def movies():
    show = Show.query.all()
    return render_template('movies.html', show=show)

@app.route('/venue')
def venue():
    venue = Venue.query.all()
    return render_template('venue.html', venue=venue)


@app.route('/search_results')
def search_results():
    query = request.args.get('query')
    
    # Search for movies and venues with matching name or tags
    movies = Show.query.filter(or_(Show.name.like(f'%{query}%'), Show.tags.like(f'%{query}%'))).all()
    venues = Venue.query.filter(or_(Venue.name.like(f'%{query}%'), Venue.address.like(f'%{query}%'))).all()
    
    return render_template('search_results.html', query=query, movies=movies, venues=venues)


# ============================================================================ Show Controlls ====================================================================
# ======= Add Shows ====================================
@app.route('/admin/add_show/<int:venue_id>', methods=['GET', 'POST'])
def add_show(venue_id):
    if request.method == 'POST':
        name = request.form.get('name')
        rating = request.form.get('rating')
        tags = request.form.get('tags')
        start_time_str = request.form['start_time']
        start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
        price = request.form.get('price')
        poster = request.files ['poster']

        filename = secure_filename(poster.filename)
        poster.save("static/"+filename)
        mimetype = poster.mimetype

        # Check if venue exists
        venue = Venue.query.filter_by(id=venue_id).first()
        if not venue:
            flash('Invalid venue ID')
            return redirect(url_for('admin_dashboard'))

        # Create new movie show
        show = Show(venue_id=venue_id, name=name, rating=rating, tags=tags, price=price, poster = filename, mimetype=mimetype, start_time=start_time)
        db.session.add(show)
        db.session.commit()

        flash('New movie show added successfully')
        return redirect(url_for('admin_dashboard'))

    # GET request, show add movie form
    venues = Venue.query.all()
    return render_template('add_show.html', venues=venues)



@app.route('/admin/shows/<int:id>/update', methods=['GET', 'POST'])
def update_show(id):
    show = Show.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form.get('name')
        rating = request.form.get('rating')
        tags = request.form.get('tags')
        price = request.form.get('price')
        poster = request.files.get('poster')
        if poster:
            filename = secure_filename(poster.filename)
            poster.save("static/" + filename)
            mimetype = poster.mimetype
            show.poster = filename
            show.mimetype = mimetype
        # Update show details
        show.name = name
        show.rating = rating
        show.tags = tags
        show.price = price
        db.session.commit()
        flash('Show updated successfully')
        return redirect(url_for('admin_dashboard'))
    return render_template('update_show.html', show=show)


@app.route('/admin/shows/<int:id>/delete', methods=['GET', 'POST'])
def delete_show(id):
    show = Show.query.get_or_404(id)
    if request.method == 'POST':
        # Confirm deletion
        db.session.delete(show)
        db.session.commit()
        flash('Show deleted successfully')
        return redirect(url_for('admin_dashboard'))
    return render_template('delete_show.html', show=show)






@app.route('/admin/add_venue', methods=['GET', 'POST'])
def add_venue():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        capacity = request.form['capacity']
       

        venue = Venue(name=name, address=address, capacity = capacity)
        db.session.add(venue)
        db.session.commit()

        return redirect(url_for('admin_dashboard'))

    return render_template('add_venue.html')

@app.route('/admin/venues/<int:v_id>/update', methods=['GET', 'POST'])
def edit_venue(v_id):
    venue = Venue.query.get_or_404(v_id)
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        capacity = request.form['capacity']
        # Update venue details
        venue.name = name
        venue.address = address
        venue.capacity = capacity
        db.session.commit()
        flash('Venue updated successfully')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_venue.html', venue=venue)

@app.route('/admin/venues/<venue_id>/delete', methods=['GET','POST'])
def delete_venue(venue_id):
    venue = Venue.query.get_or_404(venue_id)
    if request.method == 'POST':
        db.session.delete(venue)
        db.session.commit()
        flash('Venue deleted successfully')
        return redirect(url_for('admin_dashboard'))
    return render_template('delete_venue.html', venue=venue)




if __name__ == '__main__':
    app.run(debug=True)
