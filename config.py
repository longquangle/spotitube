import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SCHEDULER_API_ENABLED = True
    SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
    YOUTUBE_CLIENT_ID = os.environ.get('YOUTUBE_CLIENT_ID')
    YOUTUBE_CLIENT_SECRET = os.environ.get('YOUTUBE_CLIENT_SECRET')
    YOUTUBE_CLIENT_CONFIG = {"web": {
        "client_id" : YOUTUBE_CLIENT_ID,
        "project_id" : "spotitube0",
        "auth_uri" : "https://accounts.google.com/o/oauth2/auth",
        "token_uri" : "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url" : "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret" : YOUTUBE_CLIENT_SECRET,
        "redirect_uris" : ["http://localhost:5000/youtube_callback"]}}
