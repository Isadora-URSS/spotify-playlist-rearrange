# Spotify playlist rearranger
This is just a simple project of mine to sort my spotify playlists, since they become more and more messier as they grows.
The sorting is made by these criterias, from the most to less significant:
1. Artist name
2. Album release date
3. Album name
4. Disc number
5. Track number
6. Music name

I've made this solely to fulfill my organization needs, but I decide to publish here so I can have a decent thing in my profile.

### Usage
Create an app into Spotify api portal. Them, get both client id and client secret, and insert them in your config.py file as follows:
```python
SPOTIPY_CLIENT_ID = "youridhere"
SPOTIPY_CLIENT_SECRET = "yoursecrethere"
```
Into the developer portal, go into your app settings and set the Redirect URI to "https://127.0.0.1:9090"
After that, just run the script and a navigator popup will open asking you to authorize your app into your spotify account. This is because the script does the playlist editing in name of your app. 
Afterwards, the script will prompt you to paste the url you were directed to after authorizing into it. Paste it and you're done (I think so at least :P )
