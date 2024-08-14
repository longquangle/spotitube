# SpotiTube

## Step 1: Create Spotify app
Visit https://developer.spotify.com/dashboard to create and app set redirect URIs as ```http://localhost:5000/spotify_callback```. Under "Which API/SDKs are you planning to use?", check "Web API".\
From the app dashboard, select the button "Settings" and click "View client secret". You can set the environment variables ```SPOTIFY_CLIENT_ID``` and ```SPOTIFY_CLIENT_SECRET```.
## Step 2: Create YouTube app from Google Cloud Console
Visit https://console.cloud.google.com/ and "Select a project" to create a new project. Set the Project Name to whatever you desire (cannot be changed later). Go to the tab "APIs and Services". Select the sub-tab "Credentials". Under "CREATE CREDENTIALS", select "OAuth client ID" and "OAuth client ID". Select "Internal" if available, select "External" otherwise (external app is set to need to submit your app for verification).\
Add "App name", "User support email", and "Developer contact information" as appropriate.\
Save and continue under "ADD OR REMOVE SCOPES".\
Under "Test users", add the YouTube account that you intend on using.\
Add "API Key" under "Credentials". Select "Create OAuth client ID" and add "Authorized redirect URIs" as ```http://localhost:5000/youtube_callback```. Retreive Client ID and Client Secret from "Client ID for Web application". Set environment variables ```YOUTUBE_CLIENT_ID``` and ```YOUTUBE_CLIENT_SECRET``` as seen.
## Step 3: Run ```run.py```
Fork the repository and run ```python3 run.py``` to start the app.
