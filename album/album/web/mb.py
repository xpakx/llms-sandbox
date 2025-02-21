import requests
import time
from typing import List, Optional, Dict, Any

from album.model.album import Album
from album.model.track import Track


USER_AGENT = "LLMSForMusicSandbox/0.1 ( github.com/xpakx/llms-sandbox )"


def search_album(artist: str, title: str) -> Optional[Dict[str, Any]]:
    url = "https://musicbrainz.org/ws/2/release/"
    headers = {"User-Agent": USER_AGENT}
    params = {
        "query": f'artist:"{artist}" release:"{title}" primarytype:"Album" status:"Official"',
        "fmt": "json",
        "limit": 1
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['releases']:
            return data['releases'][0]
    return None


def get_tracks(release_id: str) -> Optional[Dict[str, Any]]:
    url = f"https://musicbrainz.org/ws/2/release/{release_id}"
    headers = {"User-Agent": USER_AGENT}
    params = {
        "fmt": "json",
        "inc": "recordings" 
    }
    release_response = requests.get(url, params=params, headers=headers)
    
    if release_response.status_code == 200:
        release_data = release_response.json()
        return release_data['media'][0]
    return None


def get_album_cover(id: str) -> Optional[str]:
    url = f"https://coverartarchive.org/release/{id}"
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    data = response.json()
    covers = data.get('images', [])
    if len(covers) == 0:
        return None
    cover = covers[0].get('thumbnails', {})
    size_preferences = ['500', '300', 'large']
    for size in size_preferences:
        if size in cover:
            return cover[size ]
    return None


def search_albums_by_artist(artist: str, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
    url = "https://musicbrainz.org/ws/2/release-group/"
    headers = {"User-Agent": USER_AGENT}
    params = {
        "query": f'artist:"{artist}" primarytype:"Album" status:"Official"',
        "fmt": "json",
        "limit": limit
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get('release-groups'):
            return data['release-groups']
    return None


def get_mb_album(artist: str, title: str) -> Optional[Album]:
    print(f"Fetching album: {artist} - {title}.")
    album = search_album(artist, title)

    if album and album['id']:
        title_fetched = album['title']
        artist_fetched = album['artist-credit'][0]['name']
        date = album.get('first-release-date', album.get('date', '1970-01-01')) # TODO
        release_type = album['release-group']['primary-type'] if 'primary-type' in album['release-group'] else ""
        label = album['label-info'][0]['label']['name']

        time.sleep(1)
        tracks_data = get_tracks(album['id'])
        tracks = [
            Track(number=track['number'], title=track['title'], length=track['length'])
            for track in tracks_data['tracks']
        ]
    else:
        print("Album not found in MusicBrainz")
        return None


    time.sleep(1)
    cover = get_album_cover(album['id'])

    return Album(
        title=title_fetched,
        artist=artist_fetched,
        date=date,
        release_type=release_type,
        label=label,
        tracks=tracks,
        genres=[],
        tags=[],
        cover_url=cover
    )
