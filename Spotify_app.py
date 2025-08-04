import os
import json
import threading
import requests
import keyboard
from flask import Flask, request, redirect, session
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "default_secret")

# Spotify API credentials
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:5000/callback")
PORT = int(os.getenv("PORT", 5000))

# Spotify API endpoints
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"

SCOPE = "user-modify-playback-state user-read-playback-state"

# Authorization parameters
auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "client_id": CLIENT_ID
}

# Flask Routes

@app.route("/")
def index():
    if "access_token" not in session:
        return redirect("/login")
    return "Spotify Controller is running and authenticated!"

@app.route("/login")
def login():
    url_args = "&".join([f"{key}={quote(val)}" for key, val in auth_query_parameters.items()])
    auth_url = f"{SPOTIFY_AUTH_URL}/?{url_args}"
    return redirect(auth_url)

@app.route("/callback")
def callback():
    auth_token = request.args.get("code")
    code_payload = {
        "grant_type": "authorization_code",
        "code": auth_token,
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)
    response_data = post_request.json()

    session['access_token'] = response_data.get("access_token")
    session['refresh_token'] = response_data.get("refresh_token")
    session['expires_in'] = response_data.get("expires_in")

    return redirect("/")

def get_auth_header():
    return {"Authorization": f"Bearer {session['access_token']}"}

@app.route("/play", methods=["POST"])
def play():
    r = requests.put(f"{SPOTIFY_API_BASE_URL}/me/player/play", headers=get_auth_header())
    return {"status": r.status_code}

@app.route("/pause", methods=["POST"])
def pause():
    r = requests.put(f"{SPOTIFY_API_BASE_URL}/me/player/pause", headers=get_auth_header())
    return {"status": r.status_code}

@app.route("/next", methods=["POST"])
def next_track():
    r = requests.post(f"{SPOTIFY_API_BASE_URL}/me/player/next", headers=get_auth_header())
    return {"status": r.status_code}

# Keyboard Listener

def listen_for_keys():
    print("Listening for keys: SPACE = play, P = pause, N = next")
    while True:
        try:
            if keyboard.is_pressed('space'):
                requests.post("http://localhost:5000/play")
                keyboard.wait('space')
            elif keyboard.is_pressed('p'):
                requests.post("http://localhost:5000/pause")
                keyboard.wait('p')
            elif keyboard.is_pressed('n'):
                requests.post("http://localhost:5000/next")
                keyboard.wait('n')
        except:
            pass

# Run App and Listener

if __name__ == "__main__":
    key_thread = threading.Thread(target=listen_for_keys, daemon=True)
    key_thread.start()
    app.run(debug=False, port=PORT)
