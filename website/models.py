from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    # in sql the User class will be stored in lower caps, hence user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Crypto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coin_sold = db.Column(db.String(10))
    amount_sold = db.Column(db.Integer)
    coin_bought = db.Column(db.String(10))
    amount_bought = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    #  Need capital for this one for some reason.
    notes = db.relationship('Note')
    coins = db.relationship('Crypto')
