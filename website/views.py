from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
from .models import User, Song, Artist, user_artist_rating, user_song_rating, song_artist_association_table
import itertools
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
SPOTIPY_CLIENT_ID = "342f3c7ab58c4d66bedf8d8c9fef5197"
SPOTIPY_CLIENT_SECRET = "27265d2f28694831b8ef070f131dfc2f"


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

                #check if the artist/artists are already associated with the song

                return render_template('home.html.j2', user=current_user, tracks=tracks, name_track = name_track, name_artist = name_artist)
        else: # ricerca artista
            q="artist:" + str(artist_input)
            results = sp.search(q, limit=1, type="artist")
            
            if len(results['artists']['items']) == 0:
                flash('The artist '+ str(artist_input) +' does not exist', category='error')
            else:
                artist_id = results['artists']['items'][0]['id']
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
    user_song = db.session.query(user_song_rating)
    return render_template("provadb.html.j2", user=current_user, list_user=users, songs = songs, user_song = user_song)

@views.route('/history', methods=['GET', 'POST'])
@login_required
def history(): # prendere le canzoni/artisti di ogni utente e il rispettivo voto
    ratings = db.session.query(user_song_rating.c.rating, Song.name, Song.id).join(Song).filter(user_song_rating.c.user_id == current_user.id).order_by(Song.name.asc()).all()
    if request.method == 'POST':
        for rating in ratings:
            new_rating = request.form.get(rating.id)
            user_song_association = db.session.query(user_song_rating).filter_by(user_id=current_user.id, song_id=rating.id).first()
            if user_song_association.rating != new_rating:
                db.session.query(user_song_rating).filter_by(user_id=current_user.id, song_id=rating.id).update({"rating": new_rating})
                db.session.commit()
            ratings = db.session.query(user_song_rating.c.rating, Song.name, Song.id).join(Song).filter(user_song_rating.c.user_id == current_user.id).order_by(Song.name.asc()).all()

    return render_template("history.html.j2", user=current_user, ratings=ratings)


    