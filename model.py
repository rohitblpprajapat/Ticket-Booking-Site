from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer(), nullable=False)
    shows = db.relationship('Show', backref='venue', lazy=True)
    

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    rating = db.Column(db.String, nullable=False)
    tags = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    poster = db.Column(db.Text, unique = True, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    tickets = db.relationship('Ticket', backref='show', lazy=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    tickets = db.relationship('Ticket', backref='user', lazy=True)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    