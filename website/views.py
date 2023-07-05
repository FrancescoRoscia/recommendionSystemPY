from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user, logout_user
from . import db
from .models import User, Song, Artist, user_artist_rating, user_song_rating, song_artist_association_table
import itertools
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
SPOTIPY_CLIENT_ID = "INSERT_ID"
SPOTIPY_CLIENT_SECRET = "INSERT_SECRET"


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        song = request.form.get('song')#Gets the song from the HTML
        artist_input = request.form.get('artist')
        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET))

        if song: # ricerca canzone
            q="track:" + str(song)
            results = sp.search(q, type='track')
            if len(results['tracks']['items']) == 0:
                flash('The song '+ str(song) +' does not exist', category='error')
            else:
                track_id = str(results['tracks']['items'][0]['id'])
                name_track = str(results['tracks']['items'][0]['name'])
                name_artist = results['tracks']['items'][0]['artists'][0]['name']
                recommendations = sp.recommendations(seed_tracks=[track_id], limit=10)
                tracks = recommendations['tracks']
                artists_id = []

                for i in range(len(results['tracks']['items'][0]['artists'])):
                    artists_id.append(results['tracks']['items'][0]['artists'][i]['id'])

                #add the track to the Song Table if it does not exist
                song_name = Song.query.filter_by(id = track_id).first()
                if song_name == None:
                    new_song = Song(id=track_id ,name=name_track)
                    db.session.add(new_song)
                    db.session.commit()
                
                #check if the user is already associated with the song. If not, add the user and the song (rating will be updated later)
                user_song_association = db.session.query(user_song_rating).filter_by(user_id=current_user.id, song_id=track_id).first()
                if user_song_association == None:
                    new_song_for_user = user_song_rating.insert().values(user_id=current_user.id, song_id=track_id)
                    db.session.execute(new_song_for_user)
                    db.session.commit()

                for artist_id in artists_id:
                    artist_found = Artist.query.filter_by(id = artist_id).first()
                    if artist_found == None:
                        artist = sp.artist(artist_id)
                        new_artist = Artist(id=artist_id ,name=artist['name'], genre=artist['genres'][0])
                        db.session.add(new_artist)
                        db.session.commit()

                    user_artist_association = db.session.query(user_artist_rating).filter_by(user_id=current_user.id, artist_id=artist_id).first()
                    if user_artist_association == None:
                        new_artist_for_user = user_artist_rating.insert().values(user_id=current_user.id, artist_id=artist_id)
                        db.session.execute(new_artist_for_user)
                        db.session.commit()

                    song_artist_association = db.session.query(song_artist_association_table).filter_by(artist_id=artist_id, song_id=track_id).first()
                    if song_artist_association == None:
                        new_song_for_artist = song_artist_association_table.insert().values(artist_id=artist_id, song_id=track_id)
                        db.session.execute(new_song_for_artist)
                        db.session.commit()

                

                #check if the artist/artists are already associated with the song

                return render_template('home.html.j2', user=current_user, tracks=tracks, name_track = name_track, name_artist = name_artist)
        else: # ricerca artista
            q="artist:" + str(artist_input)
            results = sp.search(q, limit=1, type="artist")
            
            if len(results['artists']['items']) == 0:
                flash('The artist '+ str(artist_input) +' does not exist', category='error')
            else:
                artist_id = results['artists']['items'][0]['id']
                artist_name = results['artists']['items'][0]['name']
                artist_genre = results['artists']['items'][0]['genres'][0]

                artist_found = Artist.query.filter_by(id = artist_id).first()
                if artist_found == None:
                    new_artist = Artist(id=artist_id ,name=artist_name, genre=artist_genre)
                    db.session.add(new_artist)
                    db.session.commit()

                #check if the user is already associated with the song. If not, add the user and the song (rating will be updated later)
                user_artist_association = db.session.query(user_artist_rating).filter_by(user_id=current_user.id, artist_id=artist_id).first()
                if user_artist_association == None:
                    new_artist_for_user = user_artist_rating.insert().values(user_id=current_user.id, artist_id=artist_id)
                    db.session.execute(new_artist_for_user)
                    db.session.commit()

                recommendations = sp.artist_related_artists(artist_id)
                artists = recommendations['artists']
                artist = []
                for item in itertools.islice(artists, 5):
                    artist.append(item)
                top_tracks = sp.artist_top_tracks(artist_id, country="US")

                if len(top_tracks['tracks']) == 0:
                    flash('The artist '+ str(artist_input) +' does not exist', category='error')
                else:
                    tracks = top_tracks['tracks']
                    return render_template('home.html.j2', user=current_user, artists=artist, tracks_art = tracks, artist_input = artist_input)

    return render_template("home.html.j2", user=current_user)

@views.route('/provadb', methods=['GET']) #just for checking the date inside of the DB
def provadb():
    users = User.query.all()
    songs = Song.query.all()
    artists = Artist.query.all()
    user_song = db.session.query(user_song_rating)
    user_artist = db.session.query(user_artist_rating)
    artist_song = db.session.query(song_artist_association_table)

    return render_template("provadb.html.j2", user=current_user, list_user=users, songs = songs, artists=artists, user_song = user_song, user_artist = user_artist, artist_songs=artist_song)

@views.route('/history', methods=['GET', 'POST'])
@login_required
def history(): 
    ratings_artist = db.session.query(user_artist_rating.c.rating, Artist.name, Artist.id).join(Artist).filter(user_artist_rating.c.user_id == current_user.id).order_by(Artist.name.asc()).all()
    ratings = db.session.query(user_song_rating.c.rating, Song.name, Song.id).join(Song).filter(user_song_rating.c.user_id == current_user.id).order_by(Song.name.asc()).all()
    
    if request.method == 'POST':
        for rating in ratings:
            new_rating = request.form.get(rating.id)
            user_song_association = db.session.query(user_song_rating).filter_by(user_id=current_user.id, song_id=rating.id).first()
            if user_song_association.rating != new_rating:
                db.session.query(user_song_rating).filter_by(user_id=current_user.id, song_id=rating.id).update({"rating": new_rating})
                db.session.commit()
            ratings = db.session.query(user_song_rating.c.rating, Song.name, Song.id).join(Song).filter(user_song_rating.c.user_id == current_user.id).order_by(Song.name.asc()).all()

        for rating_artist in ratings_artist:
            new_rating = request.form.get(rating_artist.id)
            user_artist_association = db.session.query(user_artist_rating).filter_by(user_id=current_user.id, artist_id=rating_artist.id).first()
            if user_artist_association.rating != new_rating:
                db.session.query(user_artist_rating).filter_by(user_id=current_user.id, artist_id=rating_artist.id).update({"rating": new_rating})
                db.session.commit()
            ratings_artist = db.session.query(user_artist_rating.c.rating, Artist.name, Artist.id).join(Artist).filter(user_artist_rating.c.user_id == current_user.id).order_by(Artist.name.asc()).all()
        


    return render_template("history.html.j2", user=current_user, ratings=ratings, ratings_artist = ratings_artist)


@views.route('/profile', methods=['GET', 'POST']) #just for checking the date inside of the DB
def profile():
    if request.method == 'POST':
        if "form-delete" in request.form:
            user = User.query.get(current_user.id)
            user_song_association = user_song_rating.delete().where(user_song_rating.c.user_id == current_user.id)
            user_artist_association = user_artist_rating.delete().where(user_artist_rating.c.user_id == current_user.id)
            
            if user:
                # Elimina l'utente dal database
                db.session.delete(user)
                db.session.commit()
                db.session.execute(user_song_association)
                db.session.execute(user_artist_association)
                db.session.commit()
                print("Account eliminato con successo.")
                logout_user()
                return redirect(url_for('auth.login'))
        
        elif "form-password" in request.form:
            oldPass = request.form.get('oldPassword')
            newPass = request.form.get('newPassword')

            user = User.query.filter_by(id = current_user.id).first()

            if user:
                if check_password_hash(user.password, str(oldPass)):
                    new_password_cryp = generate_password_hash(str(newPass), method='sha256')
                    user.password = new_password_cryp
                    db.session.commit()
                    flash('Password Changed!', category='success')
                else:
                    flash('Your previous password is incorrect!', category='error')
        
        elif "form-username" in request.form:
            new_username = request.form.get('username')

            user = User.query.filter_by(id = current_user.id).first()

            if user:
                usern = User.query.filter(User.id != current_user.id, func.lower(User.username) == func.lower(new_username)).first()
                if usern:
                    flash('Username already exists', category='error')
                else:
                    user.username = new_username
                    db.session.commit()
                    flash('Username Changed!', category='success')
            

    return render_template("profile.html.j2", user=current_user)