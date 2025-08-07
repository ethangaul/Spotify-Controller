import os
import requests
import webbrowser
import threading
import time
from flask import Flask, request, redirect, session
from flask_session import Session
from dotenv import load_dotenv
import keyboard

load_dotenv()

# Flask setup
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET") or "defaultsecret"

# Server-side session setup
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/tmp/flask_session'
app.config['SESSION_PERMANENT'] = False
Session(app)

# Spotify API credentials
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SCOPE = "user-read-playback-state user-modify-playback-state"

# Spotify URLs
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"

def get_auth_header():
    if 'access_token' not in session:
        raise Exception("Access token not in session.")
    return {"Authorization": f"Bearer {session['access_token']}"}

@app.route("/")
def login():
    auth_url = (
        f"{SPOTIFY_AUTH_URL}?response_type=code"
        f"&client_id={CLIENT_ID}&scope={SCOPE}&redirect_uri={REDIRECT_URI}"
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Error: Authorization code not provided."

    # Request tokens
    response = requests.post(
        SPOTIFY_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )
    data = response.json()
    session["access_token"] = data["access_token"]
    session["refresh_token"] = data["refresh_token"]
    return "Authentication successful. You can now control playback via keyboard."

@app.route("/play", methods=["POST"])
def play_track():
    try:
        r = requests.put(f"{SPOTIFY_API_BASE_URL}/me/player/play", headers=get_auth_header())
        return ("", 204)
    except Exception as e:
        print("Error in /play:", e)
        return ("Error", 500)

@app.route("/pause", methods=["POST"])
def pause_track():
    try:
        r = requests.put(f"{SPOTIFY_API_BASE_URL}/me/player/pause", headers=get_auth_header())
        return ("", 204)
    except Exception as e:
        print("Error in /pause:", e)
        return ("Error", 500)

@app.route("/next", methods=["POST"])
def next_track():
    try:
        r = requests.post(f"{SPOTIFY_API_BASE_URL}/me/player/next", headers=get_auth_header())
        return ("", 204)
    except Exception as e:
        print("Error in /next:", e)
        return ("Error", 500)

def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:5000/")

def key_listener():
    print("Listening for keys: SPACE = play, P = pause, N = next")
    while True:
        try:
            if keyboard.is_pressed("space"):
                requests.post("http://localhost:5000/play")
                time.sleep(0.5)
            elif keyboard.is_pressed("p"):
                requests.post("http://localhost:5000/pause")
                time.sleep(0.5)
            elif keyboard.is_pressed("n"):
                requests.post("http://localhost:5000/next")
                time.sleep(0.5)
        except:
            pass

if __name__ == "__main__":
    threading.Thread(target=open_browser).start()
    threading.Thread(target=key_listener, daemon=True).start()
    app.run(debug=False)

