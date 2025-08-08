import os
import json
from flask import Flask, redirect, request, url_for
from flask_session import Session
from spotipy.oauth2 import SpotifyOAuth
import dotenv

dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000/callback'
SCOPE = 'user-read-playback-state user-modify-playback-state'

TOKEN_PATH = 'spotify_token.json'

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=None  # Disable default caching, we manage manually
)

def save_token(token_info):
    with open(TOKEN_PATH, 'w') as f:
        json.dump(token_info, f)

def load_token():
    if not os.path.exists(TOKEN_PATH):
        return None
    with open(TOKEN_PATH, 'r') as f:
        return json.load(f)

@app.route('/')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    save_token(token_info)
    return "Authentication successful! You can close this tab and run the key listener."

@app.route('/refresh_token')
def refresh_token():
    token_info = load_token()
    if token_info and sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        save_token(token_info)
        return "Token refreshed!"
    return "Token valid, no refresh needed."

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
