import requests
from datetime import datetime
from urllib.parse import urlencode
from flask import redirect, request, render_template, url_for
from flask_login import login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField
from wtforms.validators import InputRequired
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from spotitube import app, db
from spotitube.models import User
from spotitube import utils, scheduler

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect('/sign_in')
    return render_template('home.html')

@app.route('/sign_in')
def sign_in():
    return render_template('signIn.html', title="Sign In")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/spotify_login')
def spotify_login():
    if current_user.is_authenticated:
        return redirect('/')
    scope = 'playlist-read-private'

    params = {
        'client_id': app.config['SPOTIFY_CLIENT_ID'],
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': 'http://localhost:5000/spotify_callback',
        'show_dialog': False 
    }

    auth_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    return redirect(auth_url)

@app.route('/spotify_callback')
def spotify_callback():
    if 'code' in request.args:
        request_body = {
            'code': request.args.get('code'),
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://localhost:5000/spotify_callback',
            'client_id': app.config['SPOTIFY_CLIENT_ID'],
            'client_secret': app.config['SPOTIFY_CLIENT_SECRET']
        }

        response = requests.post('https://accounts.spotify.com/api/token', data=request_body)
        token_info = response.json()

        spotify_user_id, spotify_username = utils.spotify_get_user(token_info['access_token'])
        user = User.query.filter_by(spotify_user_id = spotify_user_id).first()
        # if the user is already in the database
        if user:
            # update keys
            user.spotify_access_token = token_info['access_token']
            user.spotify_refresh_token = token_info['refresh_token']
            user.spotify_expires_at = datetime.now().timestamp() + token_info['expires_in']
            db.session.commit()
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(url_for(next_page)) if next_page else redirect('/')
        else:
            new_user = User(spotify_user_id=spotify_user_id, 
                            spotify_username=spotify_username,
                            spotify_access_token=token_info['access_token'], 
                            spotify_refresh_token=token_info['access_token'],
                            spotify_expires_at=datetime.now().timestamp() + token_info['expires_in'])
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect('/spotify_playlists')
    return redirect('/sign_in')

@app.route('/spotify_playlists', methods = ['GET', 'POST'])
@login_required
def spotify_playlists():
    options, playlists, images = utils.spotify_get_playlists(current_user)

    # declare radio button inside after obtain the playlist
    class SelectSpotifyPlaylist(FlaskForm):
        radio = RadioField('Your Spotify playlists',
                            choices=options, 
                            validators=[InputRequired(message='Select one playlist')]) 
        selectPlaylistButton = SubmitField("Confirm change")
    form = SelectSpotifyPlaylist()

    if form.validate_on_submit():
        selected_playlist_str = form.radio.data
        delimiter_index = selected_playlist_str.find(' ')
        new_playlist_url, new_playlist_name = selected_playlist_str[:delimiter_index], selected_playlist_str[delimiter_index + 1:]
        if current_user.spotify_playlist_url != new_playlist_url or current_user.spotify_playlist_name != new_playlist_name:
            current_user.spotify_playlist_url = selected_playlist_str[:delimiter_index]
            current_user.spotify_playlist_name = selected_playlist_str[delimiter_index + 1:]
            db.session.commit()
        return redirect(url_for('spotify_songs')) if not current_user.youtube_access_token else redirect('/')
    return render_template('spotifyPlaylists.html', form = form, playlists = playlists, images = images, title="Spotify Playlists")

@app.route('/spotify_remove_playlist')
@login_required
def spotify_remove_playlist():
    if current_user.spotify_playlist_name or current_user.spotify_playlist_url:
        current_user.spotify_playlist_name = None
        current_user.spotify_playlist_url = None
        db.session.commit()
    return redirect('/')

@app.route('/spotify_songs')
@login_required
def spotify_songs():
    return render_template('spotifySongs.html', title="Spotify Songs")
    
@app.route('/youtube_login')
@login_required
def youtube_login():
    flow = InstalledAppFlow.from_client_config(app.config['YOUTUBE_CLIENT_CONFIG'], scopes = ["https://www.googleapis.com/auth/youtube"])

    flow.redirect_uri = url_for('youtube_callback', _external=True)
    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    
    return redirect(authorization_url)

@app.route('/youtube_callback')
@login_required
def youtube_callback():
    flow = InstalledAppFlow.from_client_config(app.config['YOUTUBE_CLIENT_CONFIG'], scopes = ["https://www.googleapis.com/auth/youtube"])
    flow.redirect_uri = url_for('youtube_callback', _external=True)

    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    current_user.youtube_access_token = credentials.token
    current_user.youtube_refresh_token = credentials.refresh_token
    db.session.commit()

    return redirect('/youtube_playlist')
    
@app.route('/youtube_playlist')
@login_required
def youtube_playlist():
    # requesting songs from spotify
    all_songs = utils.spotify_get_songs(current_user)

    credentials = Credentials(**utils.youtube_credentials_dict(current_user))
    if credentials.valid and credentials.expired:
        utils.youtube_refresh_token(credentials)

    youtube = build('youtube', 'v3', credentials = credentials)
    # create YouTube playlist with name from Spotify playlist, returns the playlist id of the new playlist
    if not current_user.youtube_playlist_id:
        utils.youtube_create_playlist(current_user, youtube)

    # search and ad song to playlist
    for song in all_songs:
        video_id = utils.youtube_search(song, youtube)
        # only add video if there is a search result, ignore otherwise
        # if video_id:
        #     utils.youtube_add_song(current_user, video_id, youtube)

    return render_template('youtubePlaylist.html', all_songs = all_songs, title="YouTube Playlist")

@app.route('/spotify_logout')
def spotify_logout():
    logout_user()
    return redirect('/')

@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')


# @scheduler.task('cron', id='add_new_songs', hour=1)
# def add_new_songs():
#     print('Running background task')
#     with scheduler.app.app_context():
#         users = User.query.all()
#         for user in users:
#             if (not user.spotify_access_token or 
#                 not user.spotify_refresh_token or 
#                 not user.youtube_access_token or 
#                 not user.youtube_refresh_token or 
#                 not user.youtube_playlist_id):
#                 continue
#             new_songs = utils.spotify_get_new_songs(user)
#             print(user.spotify_username, new_songs)

#             credentials = Credentials(**utils.youtube_credentials_dict(user))
#             if credentials.valid and credentials.expired:
#                 utils.youtube_refresh_token(credentials)

#             youtube = build('youtube', 'v3', credentials = credentials)

#             # search and ad song to playlist
#             for song in new_songs:
#                 video_id = utils.youtube_search(song, youtube)
#                 # only add video if there is a search result, ignore otherwise
#                 if video_id:
#                     utils.youtube_add_song(user, video_id, youtube)