import json
import requests
import time
from selectolax.parser import HTMLParser
from urllib.parse import quote


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

    print('\nLinks:')
    link = find_bandcamp_link(artist, title)
    print(link)

    time.sleep(1)
    cover = get_album_cover(album['id'])
    if cover:
        download_image(cover, "cover.jpg")


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


def find_bandcamp_link(artist, title):
    query = quote(f"{artist} {title}")
    link = f"https://bandcamp.com/search?q={query}&item_type=a"
    response = requests.get(link)
    parser =  HTMLParser(response.text)
    results = parser.css('li[class~="searchresult"] > a')
    if len(results) == 0:
        return None
    attrs = results[0].attributes
    if 'href' in attrs:
        return attrs['href'].split('?')[0]


def get_album_cover(id):
    url = f"https://coverartarchive.org/release/{id}"
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'images' in data and data['images']:
            return data['images'][0]['thumbnails']['500']
    return None


def download_image(image_url, filename):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download image: {filename}")


if __name__ == "__main__":
    get_album("Shane Parish", "Repertoire")
