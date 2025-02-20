import requests
from typing import List, Optional, Dict, Any


USER_AGENT = "LLMSForMusicSandbox/0.1 ( github.com/xpakx/llms-sandbox )"


def search_album(artist: str, title: str) -> Optional[Dict[str, Any]]:
    url = "https://musicbrainz.org/ws/2/release/"
    headers = {"User-Agent": USER_AGENT}
    params = {
        "query": f'artist:"{artist}" release:"{title}"',
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
    if response.status_code == 200:
        data = response.json()
        if 'images' in data and data['images']:
            return data['images'][0]['thumbnails']['500']
    return None


def search_albums_by_artist(artist: str, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
    url = "https://musicbrainz.org/ws/2/release-group/"
    headers = {"User-Agent": USER_AGENT}
    params = {
        "query": f'artist:"{artist}" AND primarytype:"album"',
        "fmt": "json",
        "limit": limit
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get('release-groups'):
            return data['release-groups']
    return None
