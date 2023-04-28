from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
#from .models import Note
from . import db
from .models import User
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

        if song:
            q="track:" + str(song)
            results = sp.search(q, type='track')
            if len(results['tracks']['items']) == 0:
                flash('The song '+ str(song) +' does not exist', category='error')
            else:
                track_id = results['tracks']['items'][0]['id']
                name_track = results['tracks']['items'][0]['name']
                name_artist = results['tracks']['items'][0]['artists'][0]['name']
                recommendations = sp.recommendations(seed_tracks=[track_id], limit=10)
                tracks = recommendations['tracks']
                return render_template('home.html.j2', user=current_user, tracks=tracks, name_track = name_track, name_artist = name_artist)
        else:
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
        
        
        #if len(str(note)) < 1:
        #    flash('Note is too short!', category='error') 
        #else:
        #    new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
        #    db.session.add(new_note) #adding the note to the database 
        #    db.session.commit()
        #    flash('Note added!', category='success')

    return render_template("home.html.j2", user=current_user)

@views.route('/provadb', methods=['GET']) #serve per stampare tutti gli utenti
def provadb():
    users = User.query.all()
    return render_template("provadb.html.j2", user=current_user, list_user=users)

@views.route('/songs', methods=['GET'])
@login_required
def songs(): # prendere le canzoni/artisti di ogni utente e il rispettivo voto
    return render_template("")

# @views.route('/ricevi-dati', methods=['POST'])
# def ricevi_dati():  
    """
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    
    """

    