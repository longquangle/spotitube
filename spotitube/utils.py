import requests
from datetime import datetime, UTC
from google.auth.transport.requests import Request
from spotitube import db
from spotitube.models import Song
from spotitube import app

def youtube_create_playlist(user, youtube):
    request_body = {"snippet": {"title": f"{user.spotify_playlist_name} from SpotiTube", 
                                "description": f"Playlist created by SpotiTube. Updated daily from {user.spotify_playlist_name} playlist on Spotify."},
                    "status": {"privacyStatus": "private"}}
    # keep
    request = youtube.playlists().insert(part='snippet,status', body=request_body)
    try:
        response = request.execute()
    except:
        return ''
    user.youtube_playlist_id = response['id']
    db.session.commit()
    return response['id']

def youtube_search(song, youtube):
    song_in_db = Song.query.filter_by(spotify_song_name = song).first()
    if song_in_db:
        return song_in_db.youtube_video_id
    # search
    request = youtube.search().list(
        part="snippet",
        maxResults=1,
        q=song,
        type="video"
    )
    # the id of the result video
    try:
        response = request.execute()
    except:
        return ''
    new_song = Song(spotify_song_name = song, youtube_video_id = response['items'][0]['id']['videoId'])
    db.session.add(new_song)
    db.session.commit()
    return response['items'][0]['id']['videoId']

def youtube_add_song(user, video_id, youtube):
    request_body = {"snippet": {"playlistId": user.youtube_playlist_id, "resourceId": {"videoId": video_id, "kind": "youtube#video"}}}
    request = youtube.playlistItems().insert(
        part="snippet",
        body= request_body
    )
    try:
        response = request.execute()
        return response
    except:
        return None

def youtube_credentials_dict(user):
    return {'token': user.youtube_access_token,
            'refresh_token': user.youtube_refresh_token,
            'token_uri': "https://oauth2.googleapis.com/token",
            'client_id': app.config['YOUTUBE_CLIENT_ID'],
            'client_secret':app.config['YOUTUBE_CLIENT_SECRET'],
            'scopes': ["https://www.googleapis.com/auth/youtube"]}

def youtube_refresh_token(user, credentials):
    credentials.refresh(Request())
    user.youtube_access_token = credentials.token
    user.youtube_refresh_token = credentials.refresh_token
    db.session.commit()
    return

def spotify_get_songs(user):
    if datetime.now().timestamp() > user.spotify_expires_at:
        # spotify_refresh_token(current_user)
        spotify_refresh_token(user)
    headers = {
        'Authorization': f"Bearer {user.spotify_access_token}"
    }
    params = {'fields' : 'next,items(track(name,artists.name))'}
    response = requests.get(f"{user.spotify_playlist_url}/tracks", params=params, headers=headers)
    songs = response.json()
    if 'error' in response:
        return []
    all_songs = [item['track']['name'] + ' by ' + ' '.join([artist['name'] for artist in item['track']['artists'] if artist['name']]) for item in songs['items']]
    # allowing an unlimited number of songs for now
    while songs['next']:
        response = requests.get(songs['next'], headers=headers)
        songs = response.json()
        all_songs = all_songs + [item['track']['name'] + ' ' + ' '.join([artist['name'] for artist in item['track']['artists'] if artist['name']]) for item in songs['items']]
    return all_songs

def spotify_get_new_songs(user):
    """Retrieve songs that were added to the playlist within the last 24 hours"""
    if datetime.now().timestamp() > user.spotify_expires_at:
        spotify_refresh_token(user)
    headers = {
        'Authorization': f"Bearer {user.spotify_access_token}"
    }
    params = {'fields' : 'next,items(added_at,track(name,artists.name))'}
    response = requests.get(f"{user.spotify_playlist_url}/tracks", params=params, headers=headers)
    songs = response.json()
    new_songs = []
    if 'error' in songs:
        return new_songs
    for item in songs['items']:
        if (datetime.now(UTC) - datetime.fromisoformat(item['added_at'])).days < 1:
            new_songs.append(item['track']['name'] + ' ' + ' '.join([artist['name'] for artist in item['track']['artists'] if artist['name']]))
    while songs['next']:
        response = requests.get(songs['next'], headers=headers)
        songs = response.json()
        if 'error' in songs:
            return new_songs
        for item in songs['items']:
            if (datetime.now(UTC) - datetime.fromisoformat(item['added_at'])).days < 1:
                new_songs.append(item['track']['name'] + ' ' + ' '.join([artist['name'] for artist in item['track']['artists'] if artist['name']]))
    return new_songs

def spotify_get_playlists(user):
    if datetime.now().timestamp() > user.spotify_expires_at:
        spotify_refresh_token(user)
    headers = {
        'Authorization': f"Bearer {user.spotify_access_token}"
    }
    response = requests.get("https://api.spotify.com/v1/me/playlists", params ={'limit': 50}, headers=headers)
    playlists = response.json()
    if 'error' in playlists:
        return [], {}, []
    images = [item['images'][0]['url'] for item in playlists['items']]
    return [(playlist['href'] + ' ' + playlist['name'], playlist['name']) for playlist in playlists['items']], playlists, images

def spotify_get_user(spotify_access_token):
    headers = {
        'Authorization': f"Bearer {spotify_access_token}"
    }
    
    response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    response = response.json()
    if 'error' in response:
        return '', ''
    return response.get('id'), response.get('display_name')

def spotify_refresh_token(user):
    request_body = {
        'grant_type': 'refresh_token',
        'refresh_token': user.spotify_refresh_token,
        'client_id': app.config['SPOTIFY_CLIENT_ID'],
        'client_secret': app.config['SPOTIFY_CLIENT_SECRET']
    }

    response = requests.post('https://accounts.spotify.com/api/token', data=request_body)
    new_token_info = response.json()

    if 'error' in new_token_info:
        user.spotify_access_token = None
        user.spotify_expires_at = datetime.now().timestamp()
        db.session.commit()
        return ''

    user.spotify_access_token = new_token_info['access_token']
    user.spotify_expires_at = datetime.now().timestamp() + new_token_info['expires_in']
    db.session.commit()
    return new_token_info['access_token']