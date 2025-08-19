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

# 2. Callback endpoint: Spotify redirects here after user logs in
@app.route("/spotify/callback")
def spotify_callback():
	code = request.args.get("code")
	error = request.args.get("error")
	if error:
		return f"Error: {error}", 400
	if not code:
		return "No code provided", 400

	# Exchange code for access token
	token_url = "https://accounts.spotify.com/api/token"
	payload = {
		"grant_type": "authorization_code",
		"code": code,
		"redirect_uri": SPOTIFY_REDIRECT_URI,
		"client_id": SPOTIFY_CLIENT_ID,
		"client_secret": SPOTIFY_CLIENT_SECRET
	}
	headers = {"Content-Type": "application/x-www-form-urlencoded"}
	response = requests.post(token_url, data=payload, headers=headers)
	if response.status_code != 200:
		return f"Failed to get token: {response.text}", 400
	token_info = response.json()
	# Save token in session (for demo; in production, use a database or secure storage)
	session["spotify_token_info"] = token_info
	return jsonify({"message": "Spotify authentication successful!", "token_info": token_info})
