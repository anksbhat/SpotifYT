from flask import Flask, redirect, request, session, url_for, jsonify
import os
import requests
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev")  # Needed for session

# Spotify API credentials from environment variables
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")

# Spotify scopes: what permissions we want from the user
SPOTIFY_SCOPE = "playlist-read-private playlist-read-collaborative user-library-read"

# --- YouTube OAuth Endpoints ---
# These endpoints allow the user to authenticate with their Google account for YouTube Data API access.
YOUTUBE_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REDIRECT_URI = os.environ.get("YOUTUBE_REDIRECT_URI")
YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"

# 1. YouTube login endpoint: redirects user to Google's OAuth consent screen
# (Implementation for YouTube login endpoint should be added here if needed)

# --- Endpoints ---

# Endpoint to fetch tracks from a given Spotify playlist
@app.route("/spotify/playlist/<playlist_id>/tracks")
def get_spotify_playlist_tracks(playlist_id):
	# Get token info from session (in production, use a database or secure storage)
	token_info = session.get("spotify_token_info")
	if not token_info or "access_token" not in token_info:
		return {"error": "User not authenticated with Spotify."}, 401

	access_token = token_info["access_token"]
	# Call Spotify API to get tracks from the playlist
	headers = {"Authorization": f"Bearer {access_token}"}
	tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
	response = requests.get(tracks_url, headers=headers)
	if response.status_code != 200:
		return {"error": "Failed to fetch playlist tracks.", "details": response.text}, 400
	tracks = response.json()
	return tracks

# Endpoint to fetch user's Spotify playlists using the access token (with pagination)
@app.route("/spotify/playlists")
def get_spotify_playlists():
	# Get token info from session (in production, use a database or secure storage)
	token_info = session.get("spotify_token_info")
	if not token_info or "access_token" not in token_info:
		return {"error": "User not authenticated with Spotify."}, 401

	access_token = token_info["access_token"]
	headers = {"Authorization": f"Bearer {access_token}"}
	playlists_url = "https://api.spotify.com/v1/me/playlists"
	all_playlists = []
	url = playlists_url
	# Fetch all pages of playlists
	while url:
		response = requests.get(url, headers=headers)
		if response.status_code != 200:
			return {"error": "Failed to fetch playlists.", "details": response.text}, 400
		data = response.json()
		all_playlists.extend(data.get("items", []))
		url = data.get("next")
	# Return just the playlist names and IDs for easier debugging
	result = [{"name": p["name"], "id": p["id"]} for p in all_playlists]
	return {"total": len(result), "playlists": result}

@app.route("/")
def home():
	return {"message": "SpotifYT Flask API is running."}

# 1. Login endpoint: redirects user to Spotify's authorization page
@app.route("/spotify/login")
def spotify_login():
	params = {
		"client_id": SPOTIFY_CLIENT_ID,
		"response_type": "code",
		"redirect_uri": SPOTIFY_REDIRECT_URI,
		"scope": SPOTIFY_SCOPE,
		"show_dialog": "true"
	}
	url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
	return redirect(url)
