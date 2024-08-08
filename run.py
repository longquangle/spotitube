from spotitube import app

"""WARNING: FOR DEPLOYMENT, TURN OFF DEBUG MODE AND TURN OFF os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'"""

if __name__ == '__main__':
    # app.run(host='0.0.0.0', debug=True, use_reloader=False)
    app.run(host='0.0.0.0', debug=True)



# sample response for youtube_create_playlist
# {'kind': 'youtube#playlist', 
#  'etag': 'KF4jMNqhTkKmLbsmELMKhNg44FA', 
#  'id': 'PLl7U9bFz54UfGkradu4OL0goJLs9rIO6c', 
#  'snippet': {'publishedAt': '2024-02-27T05:41:04Z', 
#              'channelId': 'UCpax29NoNmjDwatCCV1Orzg', 
#              'title': 'My 2023 Playlist in a Bottle from SpotiTube', 
#              'description': 'Playlist created by SpotiTube. Updated daily from My 2023 Playlist in a Bottle playlist on Spotify.', 
#              'thumbnails': {'default': {'url': 'https://i.ytimg.com/img/no_thumbnail.jpg', 'width': 120, 'height': 90}, 
#                             'medium': {'url': 'https://i.ytimg.com/img/no_thumbnail.jpg', 'width': 320, 'height': 180}, 
#                             'high': {'url': 'https://i.ytimg.com/img/no_thumbnail.jpg', 'width': 480, 'height': 360}}, 
#                             'channelTitle': 'Long Le', 
#                             'defaultLanguage': 'en', 
#                             'localized': 
#                             {'title': 'My 2023 Playlist in a Bottle from SpotiTube', 'description': 'Playlist created by SpotiTube. Updated daily from My 2023 Playlist in a Bottle playlist on Spotify.'}}, 
#                             'status': {'privacyStatus': 'private'}}
    
