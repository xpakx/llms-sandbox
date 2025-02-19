import json
import requests
import time


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
        print(title)
        print(f"by {artist}\n")
        print(f"Released: {album['date']}")
        print(album['release-group']['primary-type'])
        print(f"Label: {album['label-info'][0]['label']['name']}")

        time.sleep(1)
        tracks = get_tracks(album['id'])
        print('\nTracklist:')
        for track in tracks['tracks']:
            no = track['number']
            song = track['title']
            seconds = int(track['length']) // 1000
            minutes, seconds = divmod(seconds, 60)
            printlen = f"{minutes:02d}:{seconds:02d}"
            print(f"{no}. {song} ({printlen})")

    else:
        print("Album not found in MusicBrainz")


def get_tracks(release_id: str):
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



if __name__ == "__main__":
    get_album("Shane Parish", "Repertoire")
