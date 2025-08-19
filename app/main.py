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
@app.route("/youtube/login")
def youtube_login():
	params = {
		"client_id": YOUTUBE_CLIENT_ID,
		"redirect_uri": YOUTUBE_REDIRECT_URI,
		"response_type": "code",
		"scope": YOUTUBE_SCOPE,
		"access_type": "offline",
		"prompt": "consent"
	}
	url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
	return redirect(url)

# 2. YouTube callback endpoint: Google redirects here after user logs in
@app.route("/youtube/callback")
def youtube_callback():
	code = request.args.get("code")
	error = request.args.get("error")
	if error:
		return f"Error: {error}", 400
	if not code:
		return "No code provided", 400

	# Exchange code for access token
	token_url = "https://oauth2.googleapis.com/token"
	payload = {
		"code": code,
		"client_id": YOUTUBE_CLIENT_ID,
		"client_secret": YOUTUBE_CLIENT_SECRET,
		"redirect_uri": YOUTUBE_REDIRECT_URI,
		"grant_type": "authorization_code"
	}
	headers = {"Content-Type": "application/x-www-form-urlencoded"}
	response = requests.post(token_url, data=payload, headers=headers)
	if response.status_code != 200:
		return f"Failed to get token: {response.text}", 400
	token_info = response.json()
	# Save token in session (for demo; in production, use a database or secure storage)
	session["youtube_token_info"] = token_info
	return jsonify({"message": "YouTube authentication successful!", "token_info": token_info})

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
