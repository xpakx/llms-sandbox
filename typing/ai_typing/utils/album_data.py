import json
import requests
import time
from selectolax.parser import HTMLParser
from urllib.parse import quote
from string import Template
from pathlib import Path


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
        date = album['date']
        print(f"Released: {date}")
        release_type = album['release-group']['primary-type']
        print(release_type)
        label = album['label-info'][0]['label']['name']
        print(f"Label: {label}")

        time.sleep(1)
        tracks = get_tracks(album['id'])
        tracks_str = ""
        print('\nTracklist:')
        for track in tracks['tracks']:
            no = track['number']
            song = track['title']
            seconds = int(track['length']) // 1000
            minutes, seconds = divmod(seconds, 60)
            printlen = f"{minutes:02d}:{seconds:02d}"
            print(f"{no}. {song} ({printlen})")
            tracks_str += f"<li>{no}. {song} ({printlen})</li>\n"

    else:
        print("Album not found in MusicBrainz")
        return

    print('\nLinks:')
    link = find_bandcamp_link(artist, title)
    print(link)

    time.sleep(1)
    cover = get_album_cover(album['id'])

    Path("dist").mkdir(exist_ok=True)
    if cover:
        download_image(cover, "dist/cover.jpg")
    genres = "<span>american primitivism</span>\n<span>folk</span>"
    tags = "<span>#fingerpicking</span>\n<span>#solo guitar</span>"
    description = "Shane Parish's <em>Repertoire</em> is a stunning collection of reimagined classics, showcasing his virtuosic guitar work and unique interpretive style."
    html = generate_html(artist, title, date, tracks_str, "★ ★ ★ ½", genres, tags, description)
    saveTo(html, "dist/index.html")


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


def generate_html(artist, title, date, tracks, rating, genres, tags, description) -> str:
    with open('files/index.html', 'r') as file:
        content = file.read()
    template = Template(content)
    return template.substitute(
            artist=artist,
            title=title,
            date=date,
            tracks=tracks,
            rating=rating,
            genres=genres,
            tags=tags,
            description=description)


def saveTo(data: str, filename: str):
    f = open(filename, "w")
    f.write(data)
    f.close()

if __name__ == "__main__":
    get_album("Shane Parish", "Repertoire")
