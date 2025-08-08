🎵 Spotify Controller

Control Spotify playback using physical keyboard keys or keyboard emulator (on a Raspberry Pi):
- `O` → Play
- `P` → Pause
- `N` → Next track
  
Designed to be used with a keystroke module attached to snowboarding glove

View the progress on my LinkedIn! [[https://www.linkedin.com/in/ethan-gaul/](https://www.linkedin.com/in/ethan-gaul/details/projects/)]

TO USE:
-------
1. Set up Spotify app on Spotify Developer Dashboard [https://developer.spotify.com/dashboard]
2. Clone the repository

  ```bash
  git clone https://github.com/ethangaul/Spotify-Glove.git/
  cd Spotify-Glove
  ```

3. Fill in .env files with your credentials
4. Install dependancies:

  ```bash
  pip install -r requirements.txt
  ```
   
5. Run the spotify account authentication:
  ```bash
  python3 auth_server.py
  ```

6. Sign into your Spotify account
7. Close the auth_server.py and run the key listener:
  ```bash
  python3 key_listener.py
  ```

**FREE to use** -- please credit [https://github.com/ethangaul/] for all referencing.

🎬Video of code application and use: [https://vimeo.com/1108283956?share=copy]
