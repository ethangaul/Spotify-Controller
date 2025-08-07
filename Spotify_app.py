import os
import threading
from flask import Flask, redirect, request, session, jsonify
from flask_session import Session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pynput import keyboard
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./.flask_session/"
Session(app)

# Spotify API credentials
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SCOPE = "user-read-playback-state user-modify-playback-state"

# Spotify OAuth object
sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
)

# Helper: Get Spotify client from session
def get_spotify_client():
    token_info = session.get("token_info", None)
    if not token_info:
        return None
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["token_info"] = token_info
    return spotipy.Spotify(auth=token_info["access_token"])

@app.route("/")
def index():
    return redirect("/login")

@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    print("✅ Authentication successful. You can now control playback via keyboard.")
    return "Authentication successful. You can now control playback via keyboard."

@app.route("/play")
def play():
    sp = get_spotify_client()
    if sp:
        sp.start_playback()
        return jsonify({"status": "playing"})
    return jsonify({"error": "Access token not in session"}), 401

@app.route("/pause")
def pause():
    sp = get_spotify_client()
    if sp:
        sp.pause_playback()
        return jsonify({"status": "paused"})
    return jsonify({"error": "Access token not in session"}), 401

@app.route("/next")
def next_track():
    sp = get_spotify_client()
    if sp:
        sp.next_track()
        return jsonify({"status": "next"})
    return jsonify({"error": "Access token not in session"}), 401

# Keyboard listener
def on_press(key):
    try:
        if key.char == " ":
            requests.get("http://127.0.0.1:5000/play")
        elif key.char.lower() == "p":
            requests.get("http://127.0.0.1:5000/pause")
        elif key.char.lower() == "n":
            requests.get("http://127.0.0.1:5000/next")
    except AttributeError:
        pass

def start_keyboard_listener():
    from pynput import keyboard
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

if __name__ == "__main__":
    import requests
    threading.Thread(target=start_keyboard_listener, daemon=True).start()
    app.run(debug=True)
