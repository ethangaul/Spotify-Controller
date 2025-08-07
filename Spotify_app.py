import os
import json
import threading
from flask import Flask, redirect, request, session, url_for
from flask_session import Session
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pynput import keyboard

# Flask app setup
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Spotify API credentials (from environment variables)
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = 'http://localhost:5000/callback'

# OAuth scope
SCOPE = "user-read-playback-state,user-modify-playback-state"

# Spotipy OAuth
sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE
)

# Get a Spotify client with stored token
def get_spotify_client():
    token_info = session.get('token_info')
    if not token_info:
        return None
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info
    return spotipy.Spotify(auth=token_info['access_token'])

@app.route('/')
def index():
    if not session.get('token_info'):
        return redirect(url_for('login'))
    return "Authentication successful. You can now control playback via keyboard."

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    print("Token stored in session:", json.dumps(token_info, indent=2))
    return redirect(url_for('index'))

@app.route('/play')
def play():
    sp = get_spotify_client()
    if not sp:
        return "Access token not in session", 401
    sp.start_playback()
    return "Playback started"

@app.route('/pause')
def pause():
    sp = get_spotify_client()
    if not sp:
        return "Access token not in session", 401
    sp.pause_playback()
    return "Playback paused"

@app.route('/next')
def next_track():
    sp = get_spotify_client()
    if not sp:
        return "Access token not in session", 401
    sp.next_track()
    return "Skipped to next track"

# Keyboard listener
def on_press(key):
    try:
        if key.char == 'p':
            os.system("curl -s http://localhost:5000/pause")
        elif key.char == 'o':
            os.system("curl -s http://localhost:5000/play")
        elif key.char == 'n':
            os.system("curl -s http://localhost:5000/next")
    except AttributeError:
        pass

def start_key_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == '__main__':
    threading.Thread(target=start_key_listener, daemon=True).start()
    app.run(host='localhost', port=5000, debug=True)
