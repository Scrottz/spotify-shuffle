import logging
import os
import random
from pathlib import Path

from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI",
                                 "http://localhost:8888/callback")
SPOTIFY_SCOPES = [
    "user-library-read",
    "playlist-modify-public",
    "playlist-modify-private"
]
PLAYLIST_NAME = "Expendes Liked Songs"

def create_client() -> Spotify:
    return Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=" ".join(SPOTIFY_SCOPES)
    ))

def get_liked_songs(sp: Spotify) -> list:
    tracks = []
    offset = 0
    while True:
        results = sp.current_user_saved_tracks(limit=50, offset=offset)
        tracks.extend(results["items"])
        if not results["next"]:
            break
        offset += 50
    return tracks

def shuffle_tracks(tracks: list) -> list:
    shuffled = tracks.copy()
    random.shuffle(shuffled)
    return shuffled

def create_playlist_from_tracks(sp: Spotify, tracks: list,
                                name: str = PLAYLIST_NAME) -> str:
    user_id = sp.current_user()["id"]
    playlist = sp.user_playlist_create(user=user_id, name=name, public=False)

    track_uris = [item["track"]["uri"] for item in tracks]
    for i in range(0, len(track_uris), 100):
        sp.playlist_add_items(playlist["id"], track_uris[i:i+100])

    return playlist["external_urls"]["spotify"]



if __name__ == "__main__":
    sp = create_client()


    logger.info("Fetching Liked Songs")
    liked_songs = get_liked_songs(sp)
    logger.info(f"{len(liked_songs)} Tracks found")

