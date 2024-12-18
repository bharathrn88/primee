from utils.db import db

class Movies(db.Model):
    movie_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    cast = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime)
    release_date = db.Column(db.DateTime)
    rating = db.Column(db.Float)
    duration = db.Column(db.Float)
    listed_in = db.Column(db.Boolean)
    description = db.Column(db.String(120), nullable=False)


class Account(db.Model):
    email_id = db.Column(db.String(100), primary_key=True)
    mobile_number = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)

class signin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(1000), nullable=False)
    email = db.Column(db.String(100), nullable=False)

class Subscription(db.Model):
    name = db.Column(db.String(100), nullable=False)
    card_number = db.Column(db.String(1000), nullable=False)
    expiry_date = db.Column(db.String(100), nullable=False)
    cvv = db.Column(db.String(100), nullable=False)

