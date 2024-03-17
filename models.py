from spotitube import db, login_manager
from flask_login import UserMixin

"""
from spotitube import app, db
from spotitube.models import User, Song
app.app_context().push()
db.create_all()
User.query.all()
"""

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    spotify_user_id = db.Column(db.String(100))
    spotify_username = db.Column(db.String(200))
    spotify_access_token = db.Column(db.String(100))
    spotify_refresh_token = db.Column(db.String(100))
    spotify_expires_at = db.Column(db.Float)
    spotify_playlist_url = db.Column(db.String(150))
    spotify_playlist_name = db.Column(db.String(150))

    youtube_access_token = db.Column(db.String(150))
    youtube_refresh_token = db.Column(db.String(100))
    youtube_playlist_id = db.Column(db.String(100))

    def __repr__(self):
        return f"User({self.id}, '{self.spotify_user_id}', '{self.spotify_username}')"
    
class Song(db.Model):
    spotify_song_name = db.Column(db.String(500), primary_key = True)
    youtube_video_id = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Song('{self.spotify_song_name}', {self.youtube_video_id})"