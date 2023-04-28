from . import db
from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

user_song_rating = db.Table(
    'user_song_rating',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('song_id', db.String(150), db.ForeignKey('song.id'), primary_key=True),
    db.Column('rating', db.Integer)
)

user_artist_rating = db.Table(
    'user_artist_rating',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('artist_id', db.String(150), db.ForeignKey('artist.id'), primary_key=True),
    db.Column('rating', db.Integer)
)

song_artist_association_table = db.Table(
    'song_artist_association',
    db.Column('song_id', db.String(150), db.ForeignKey('song.id'), primary_key=True),
    db.Column('artist_id', db.String(150), db.ForeignKey('artist.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150), unique=True)

class Artist(db.Model):
    id = db.Column(db.String(150), primary_key=True)
    name = db.Column(db.String(150))
    genre = db.Column(db.String(150))

class Song(db.Model):
    id = db.Column(db.String(150), primary_key=True)
    name = db.Column(db.String(150))
