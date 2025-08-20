import os
from flask import Flask, redirect, request, session, url_for, jsonify, send_from_directory
import requests
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev")  # Needed for session

# Spotify API credentials from environment variables
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")
SPOTIFY_SCOPE = "playlist-read-private playlist-read-collaborative user-library-read"

# YouTube OAuth credentials
YOUTUBE_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REDIRECT_URI = os.environ.get("YOUTUBE_REDIRECT_URI")
YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
from flask import render_template

@app.route("/")
def home():
    return render_template("index.html")
# @app.route("/")
# def home():
#     return {"message": "SpotifYT Flask API is running."}

# # --- Static Privacy Policy ---
# @app.route("/static/<path:filename>")
# def static_files(filename):
#     return send_from_directory("static", filename)

# # --- Spotify OAuth ---
# @app.route("/spotify/login")
# def spotify_login():
#     params = {
#         "client_id": SPOTIFY_CLIENT_ID,
#         "response_type": "code",
#         "redirect_uri": SPOTIFY_REDIRECT_URI,
#         "scope": SPOTIFY_SCOPE,
#         "show_dialog": "true"
#     }
#     url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
#     return redirect(url)

# @app.route("/spotify/callback")
# def spotify_callback():
#     code = request.args.get("code")
#     error = request.args.get("error")
#     if error:
#         return f"Error: {error}", 400
#     if not code:
#         return "No code provided", 400

#     token_url = "https://accounts.spotify.com/api/token"
#     payload = {
#         "grant_type": "authorization_code",
#         "code": code,
#         "redirect_uri": SPOTIFY_REDIRECT_URI,
#         "client_id": SPOTIFY_CLIENT_ID,
#         "client_secret": SPOTIFY_CLIENT_SECRET,
#     }
#     headers = {"Content-Type": "application/x-www-form-urlencoded"}
#     response = requests.post(token_url, data=payload, headers=headers)
#     if response.status_code != 200:
#         return f"Failed to get token: {response.text}", 400
#     token_info = response.json()
#     session["spotify_token_info"] = token_info
#     return jsonify({"message": "Spotify authentication successful!", "token_info": token_info})

# @app.route("/spotify/playlists")
# def get_spotify_playlists():
#     token_info = session.get("spotify_token_info")
#     if not token_info or "access_token" not in token_info:
#         return {"error": "User not authenticated with Spotify."}, 401

#     access_token = token_info["access_token"]
#     headers = {"Authorization": f"Bearer {access_token}"}
#     playlists_url = "https://api.spotify.com/v1/me/playlists"
#     all_playlists = []
#     url = playlists_url
#     while url:
#         response = requests.get(url, headers=headers)
#         if response.status_code != 200:
#             return {"error": "Failed to fetch playlists.", "details": response.text}, 400
#         data = response.json()
#         all_playlists.extend(data.get("items", []))
#         url = data.get("next")
#     result = [{"name": p["name"], "id": p["id"]} for p in all_playlists]
#     return {"total": len(result), "playlists": result}

# @app.route("/spotify/playlist/<playlist_id>/tracks")
# def get_spotify_playlist_tracks(playlist_id):
#     token_info = session.get("spotify_token_info")
#     if not token_info or "access_token" not in token_info:
#         return {"error": "User not authenticated with Spotify."}, 401

#     access_token = token_info["access_token"]
#     headers = {"Authorization": f"Bearer {access_token}"}
#     tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
#     response = requests.get(tracks_url, headers=headers)
#     if response.status_code != 200:
#         return {"error": "Failed to fetch playlist tracks.", "details": response.text}, 400
#     tracks = response.json()
#     return tracks

# # --- YouTube OAuth ---
# @app.route("/youtube/login")
# def youtube_login():
#     params = {
#         "client_id": YOUTUBE_CLIENT_ID,
#         "redirect_uri": YOUTUBE_REDIRECT_URI,
#         "response_type": "code",
#         "scope": YOUTUBE_SCOPE,
#         "access_type": "offline",
#         "prompt": "consent"
#     }
#     url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
#     return redirect(url)

# @app.route("/youtube/callback")
# def youtube_callback():
#     code = request.args.get("code")
#     error = request.args.get("error")
#     if error:
#         return f"Error: {error}", 400
#     if not code:
#         return "No code provided", 400

#     token_url = "https://oauth2.googleapis.com/token"
#     payload = {
#         "code": code,
#         "client_id": YOUTUBE_CLIENT_ID,
#         "client_secret": YOUTUBE_CLIENT_SECRET,
#         "redirect_uri": YOUTUBE_REDIRECT_URI,
#         "grant_type": "authorization_code"
#     }
#     headers = {"Content-Type": "application/x-www-form-urlencoded"}
#     response = requests.post(token_url, data=payload, headers=headers)
#     if response.status_code != 200:
#         return f"Failed to get token: {response.text}", 400
#     token_info = response.json()
#     session["youtube_token_info"] = token_info
#     return jsonify({"message": "YouTube authentication successful!", "token_info": token_info})

# # --- YouTube Playlist Management ---
# @app.route("/youtube/create_playlist", methods=["POST"])
# def youtube_create_playlist():
#     token_info = session.get("youtube_token_info")
#     if not token_info or "access_token" not in token_info:
#         return {"error": "User not authenticated with YouTube."}, 401

#     access_token = token_info["access_token"]
#     data = request.get_json()
#     title = data.get("title")
#     description = data.get("description", "")
#     if not title:
#         return {"error": "Missing playlist title."}, 400

#     url = "https://www.googleapis.com/youtube/v3/playlists?part=snippet%2Cstatus"
#     headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json", "Content-Type": "application/json"}
#     payload = {
#         "snippet": {"title": title, "description": description},
#         "status": {"privacyStatus": "private"}
#     }
#     resp = requests.post(url, headers=headers, json=payload)
#     if resp.status_code != 200:
#         return {"error": "Failed to create playlist.", "details": resp.text}, 400
#     return resp.json()

# @app.route("/youtube/add_to_playlist", methods=["POST"])
# def youtube_add_to_playlist():
#     token_info = session.get("youtube_token_info")
#     if not token_info or "access_token" not in token_info:
#         return {"error": "User not authenticated with YouTube."}, 401

#     access_token = token_info["access_token"]
#     data = request.get_json()
#     playlist_id = data.get("playlist_id")
#     video_id = data.get("video_id")
#     if not playlist_id or not video_id:
#         return {"error": "Missing playlist_id or video_id."}, 400

#     url = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet"
#     headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json", "Content-Type": "application/json"}
#     payload = {
#         "snippet": {
#             "playlistId": playlist_id,
#             "resourceId": {"kind": "youtube#video", "videoId": video_id}
#         }
#     }
#     resp = requests.post(url, headers=headers, json=payload)
#     if resp.status_code != 200:
#         return {"error": "Failed to add video.", "details": resp.text}, 400
#     return resp.json()

# # --- UI Endpoints ---
# @app.route("/transfer_ui")
# def transfer_ui():
#     return '''
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <meta name="viewport" content="width=device-width, initial-scale=1.0">
#         <title>SpotifYT Transfer</title>
#         <style>
#             body { background: #111; color: #eee; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; }
#             header { background: #1db954; color: #fff; padding: 1.5em 0; text-align: center; font-size: 2em; letter-spacing: 2px; }
#             .container { max-width: 900px; margin: 2em auto; background: #181818; border-radius: 12px; box-shadow: 0 4px 24px #0008; padding: 2em; }
#             .auth-btn { background: #e50914; color: #fff; border: none; padding: 0.7em 2em; border-radius: 5px; font-size: 1em; margin: 1em 0; cursor: pointer; transition: background 0.2s; }
#             .auth-btn:hover { background: #b00610; }
#             .playlist { background: #222; border-radius: 8px; margin: 1.5em 0; padding: 1em 1.5em; box-shadow: 0 2px 8px #0004; }
#             .playlist h3 { color: #1db954; margin: 0 0 0.5em 0; }
#             .tracks { margin: 0.5em 0 1em 0; }
#             .track { color: #eee; margin: 0.2em 0; }
#             .transfer-form { display: flex; gap: 0.5em; margin-top: 0.5em; }
#             .transfer-form input { flex: 1; padding: 0.4em; border-radius: 4px; border: 1px solid #333; background: #181818; color: #fff; }
#             .transfer-form button { background: #1db954; color: #fff; border: none; padding: 0.4em 1.2em; border-radius: 4px; cursor: pointer; }
#             .transfer-form button:hover { background: #14833b; }
#             .success { color: #1db954; margin-left: 1em; }
#             .error { color: #e50914; margin-left: 1em; }
#         </style>
#     </head>
#     <body>
#         <header>SpotifYT Playlist Transfer</header>
#         <div class="container">
#             <div id="auth-section">
#                 <button class="auth-btn" onclick="window.location='/spotify/login'">Login with Spotify</button>
#                 <button class="auth-btn" onclick="window.location='/youtube/login'">Login with YouTube</button>
#                 <div id="auth-status"></div>
#             </div>
#             <div id="playlists-section" style="display:none">
#                 <h2>Your Spotify Playlists</h2>
#                 <div id="playlists"></div>
#             </div>
#         </div>
#         <script>
#         async function checkAuth() {
#             let res = await fetch('/spotify/playlists');
#             if (res.status === 401) return false;
#             let data = await res.json();
#             if (!data.playlists) return false;
#             document.getElementById('auth-section').style.display = 'none';
#             document.getElementById('playlists-section').style.display = '';
#             renderPlaylists(data.playlists);
#             return true;
#         }

#         function renderPlaylists(playlists) {
#             const container = document.getElementById('playlists');
#             container.innerHTML = '';
#             playlists.forEach(async (pl) => {
#                 let tracks = [];
#                 try {
#                     let res = await fetch(`/spotify/playlist/${pl.id}/tracks`);
#                     if (res.ok) {
#                         let tdata = await res.json();
#                         tracks = (tdata.items || []).map(item => item.track ? `${item.track.name} - ${item.track.artists.map(a=>a.name).join(', ')}` : 'Unknown');
#                     }
#                 } catch {}
#                 const div = document.createElement('div');
#                 div.className = 'playlist';
#                 div.innerHTML = `<h3>${pl.name}</h3>
#                     <div class="tracks">
#                         ${tracks.map(t => `<div class='track'>${t}</div>`).join('')}
#                     </div>
#                     <form class="transfer-form" onsubmit="return transferPlaylist(event, '${pl.id}', '${pl.name.replace(/'/g, "\\'")}')">
#                         <input name="yt_name" placeholder="YouTube Playlist Name (default: ${pl.name})">
#                         <button type="submit">Transfer to YouTube</button>
#                         <span class="success" id="success-${pl.id}" style="display:none">✔️</span>
#                         <span class="error" id="error-${pl.id}" style="display:none"></span>
#                     </form>`;
#                 container.appendChild(div);
#             });
#         }

#         async function transferPlaylist(e, playlistId, defaultName) {
#             e.preventDefault();
#             const form = e.target;
#             const ytName = form.yt_name.value || defaultName;
#             let resp = await fetch('/youtube/create_playlist', {
#                 method: 'POST',
#                 headers: {'Content-Type': 'application/json'},
#                 body: JSON.stringify({title: ytName, description: `Imported from Spotify: ${defaultName}`})
#             });
#             let data = await resp.json();
#             if (!data.id) {
#                 form.querySelector('.error').textContent = data.error || 'Failed to create playlist';
#                 form.querySelector('.error').style.display = '';
#                 return false;
#             }
#             let tracksResp = await fetch(`/spotify/playlist/${playlistId}/tracks`);
#             let tracksData = await tracksResp.json();
#             let items = tracksData.items || [];
#             for (let item of items) {
#                 let track = item.track;
#                 if (!track) continue;
#                 let q = encodeURIComponent(track.name + ' ' + (track.artists.map(a=>a.name).join(' ')));
#                 // NOTE: Replace 'YOUR_YOUTUBE_API_KEY' with your actual API key or move this search to backend for security!
#                 let ytRes = await fetch(`https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=1&q=${q}&key=YOUR_YOUTUBE_API_KEY`);
#                 let ytJson = await ytRes.json();
#                 let videoId = ytJson.items && ytJson.items[0] && ytJson.items[0].id && ytJson.items[0].id.videoId;
#                 if (videoId) {
#                     await fetch('/youtube/add_to_playlist', {
#                         method: 'POST',
#                         headers: {'Content-Type': 'application/json'},
#                         body: JSON.stringify({playlist_id: data.id, video_id: videoId})
#                     });
#                 }
#             }
#             form.querySelector('.success').style.display = '';
#             form.querySelector('.error').style.display = 'none';
#             return false;
#         }

#         checkAuth();
#         </script>
#     </body>
#     </html>
#     '''

# @app.route("/youtube_ui")
# def youtube_ui():
#     return '''
#     <html><head><title>YouTube Playlist Tools</title></head><body style="font-family:sans-serif;max-width:600px;margin:2em auto;">
#     <h2>Create YouTube Playlist</h2>
#     <form id="createForm">
#         <input name="title" placeholder="Playlist Title" required><br>
#         <input name="description" placeholder="Description"><br>
#         <button type="submit">Create Playlist</button>
#     </form>
#     <pre id="createResult"></pre>
#     <hr>
#     <h2>Add Video to Playlist</h2>
#     <form id="addForm">
#         <input name="playlist_id" placeholder="Playlist ID" required><br>
#         <input name="video_id" placeholder="YouTube Video ID" required><br>
#         <button type="submit">Add Video</button>
#     </form>
#     <pre id="addResult"></pre>
#     <script>
#     document.getElementById('createForm').onsubmit = async function(e) {
#         e.preventDefault();
#         const title = this.title.value;
#         const description = this.description.value;
#         const res = await fetch('/youtube/create_playlist', {
#             method: 'POST',
#             headers: {'Content-Type': 'application/json'},
#             body: JSON.stringify({title, description})
#         });
#         document.getElementById('createResult').textContent = await res.text();
#     };
#     document.getElementById('addForm').onsubmit = async function(e) {
#         e.preventDefault();
#         const playlist_id = this.playlist_id.value;
#         const video_id = this.video_id.value;
#         const res = await fetch('/youtube/add_to_playlist', {
#             method: 'POST',
#             headers: {'Content-Type': 'application/json'},
#             body: JSON.stringify({playlist_id, video_id})
#         });
#         document.getElementById('addResult').textContent = await res.text();
#     };
#     </script>
#     </body></html>
#     '''