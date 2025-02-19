import json
import requests


USER_AGENT = "LLMSForMusicSandbox/0.1 ( github.com/xpakx/llms-sandbox )"


def search_album(artist, title):
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


def get_album(artist: str, title: str):
    print(f"Fetching album: {artist} - {title}.")
    album = search_album(artist, title)

    if album and album['id']:
        print(album)
    else:
        print("Album not found in MusicBrainz")


if __name__ == "__main__":
    get_album("Shane Parish", "Repertoire")
