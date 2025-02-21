import requests
from base64 import b64encode
from urllib.parse import quote
from typing import Dict, Any, Optional
import json

from album.model.track import Track
from album.model.album import Album


SPOTIFY_AUTH_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"


def get_spotify_access_token(client_id: str, client_secret: str) -> str:
    auth_header = b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
    }
    data = {
        "grant_type": "client_credentials",
    }

    response = requests.post(SPOTIFY_AUTH_URL, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def search_spotify_album(access_token: str, artist: str, title: str) -> Optional[Dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    query = quote(f"artist:{artist} album:{title}")
    url = f"{SPOTIFY_API_BASE_URL}/search?q={query}&type=album&limit=1"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    items = response.json()['albums']['items']
    if len(items) == 0:
        return None
    return items[0]


def get_spotify_album_tracks(access_token: str, album_id: str) -> list:
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    url = f"{SPOTIFY_API_BASE_URL}/albums/{album_id}/tracks"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["items"]


def get_album_details(access_token: str, album_id: str) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    url = f"{SPOTIFY_API_BASE_URL}/albums/{album_id}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_spotify_album(config: Dict[str, str], artist: str, title: str) -> Optional[Album]:
    access_token = get_spotify_access_token(config['spotifyId'], config['spotifySecret'])
    album = search_spotify_album(access_token, artist, title)
    if not album:
        return None
    spotify_url = f"https://open.spotify.com/album/{album['id']}"
    date_published = album['release_date']
    fetched_title = album['name']
    fetched_artist = album['artists'][0]['name']

    album_details = get_album_details(access_token, album['id'])
    label = album_details['label']
    tracks_data = album_details['tracks']['items']
    tracks = [
        Track(
            number=str(track['track_number']),
            title=track['name'],
            length=track['duration_ms'])
        for track in tracks_data
    ]
    genres = album_details['genres']

    return Album(
        title=fetched_title,
        artist=fetched_artist,
        date=date_published,
        release_type="Album",
        label=label,
        tracks=tracks,
        genres=genres,
        tags=[],
        cover_url=None,
        bandcamp_link=spotify_url # TODO
    )
