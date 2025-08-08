import json
import time
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from pynput import keyboard
import dotenv

dotenv.load_dotenv()

TOKEN_PATH = 'spotify_token.json'
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000/callback'
SCOPE = 'user-read-playback-state user-modify-playback-state'

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=None
)

def load_token():
    if not os.path.exists(TOKEN_PATH):
        print("Token file not found. Please authenticate first via auth_server.py.")
        return None
    with open(TOKEN_PATH, 'r') as f:
        return json.load(f)

def save_token(token_info):
    with open(TOKEN_PATH, 'w') as f:
        json.dump(token_info, f)

def get_spotify_client():
    token_info = load_token()
    if not token_info:
        return None

    if sp_oauth.is_token_expired(token_info):
        print("Refreshing token...")
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        save_token(token_info)

    return Spotify(auth=token_info['access_token'])

def on_press(key):
    sp = get_spotify_client()
    if not sp:
        print("Spotify client not ready. Authenticate first.")
        return

    try:
        if key.char == 'p':
            sp.pause_playback()
            print("Paused playback")
        elif key.char == ' ':
            sp.start_playback()
            print("Started playback")
        elif key.char == 'n':
            sp.next_track()
            print("Skipped to next track")
    except AttributeError:
        pass  # Special keys like shift or ctrl ignored

def main():
    print("Starting key listener: SPACE=play, P=pause, N=next")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == '__main__':
    main()
