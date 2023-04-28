from . import db
from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

user_song_vote = db.Table(
    'user_song_vote',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'), primary_key=True),
    db.Column('vote', db.Integer)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150), unique=True)
    songs = db.relationship('Song', secondary=user_song_vote, backref='1')
    votes = db.relationship('Song', secondary=user_song_vote, backref='2')

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    artists = db.Column(db.String(150))
    users = db.relationship('User', secondary=user_song_vote, backref='3')
    voters = db.relationship('User', secondary=user_song_vote, backref='4')
