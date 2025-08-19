
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

SCOPE = "playlist-read-private playlist-read-collaborative user-library-read"

def get_spotify_oauth():
	return SpotifyOAuth(
		client_id=SPOTIFY_CLIENT_ID,
		client_secret=SPOTIFY_CLIENT_SECRET,
		redirect_uri=SPOTIFY_REDIRECT_URI,
		scope=SCOPE
	)

def get_auth_url():
	sp_oauth = get_spotify_oauth()
	return sp_oauth.get_authorize_url()

def get_token(code):
	sp_oauth = get_spotify_oauth()
	token_info = sp_oauth.get_access_token(code)
	return token_info

def get_user_playlists(token):
	sp = spotipy.Spotify(auth=token)
	playlists = sp.current_user_playlists()
	return playlists
