import json
import requests
import time
from selectolax.parser import HTMLParser
from urllib.parse import quote
from string import Template
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


USER_AGENT = "LLMSForMusicSandbox/0.1 ( github.com/xpakx/llms-sandbox )"


class Track(BaseModel):
    number: int
    title: str
    length: int  # Length in milliseconds

    def formatted_length(self) -> str:
        minutes, seconds = divmod(self.length // 1000, 60)
        return f"{minutes:02d}:{seconds:02d}"


class Album(BaseModel):
    artist: str
    title: str
    date: str
    release_type: str
    label: str
    tracks: List[Track]
    genres: List[str]
    tags: List[str]
    cover_url: Optional[str]
    bandcamp_link: Optional[str] = None

    def formatted_date(self) -> str:
        date_obj = datetime.strptime(self.date, "%Y-%m-%d")
        return date_obj.strftime("%B %d, %Y")

    def formatted_tracks(self) -> str:
        return "".join(f"<li>{track.number}. {track.title} ({track.formatted_length()})</li>\n" for track in self.tracks)

    def formatted_tags(self) -> str:
       return generate_items(self.tags)

    def formatted_genres(self) -> str:
       return generate_items(self.genres)


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


def get_album(artist: str, title: str) -> Optional[Album]:
    print(f"Fetching album: {artist} - {title}.")
    album = search_album(artist, title)

    if album and album['id']:
        date = album['date']
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

    bandcamp_link = find_bandcamp_link(artist, title)

    time.sleep(1)
    cover = get_album_cover(album['id'])

    return Album(
        title=title,
        artist=artist,
        date=date,
        release_type=release_type,
        label=label,
        tracks=tracks,
        genres=["american primitivism", "folk"],
        tags=["fingerpicking", "solo guitar"],
        cover_url=cover,
        bandcamp_link=bandcamp_link
    )


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


def find_bandcamp_link(artist: str, title: str) -> str:
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


def get_album_cover(id: str) -> Optional[str]:
    url = f"https://coverartarchive.org/release/{id}"
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'images' in data and data['images']:
            return data['images'][0]['thumbnails']['500']
    return None


def download_image(image_url: str, filename: str) -> None:
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download image: {filename}")


def generate_html(album: Album, rating: str, description: str) -> str:
    with open('files/index.html', 'r') as file:
        content = file.read()
    template = Template(content)
    return template.substitute(
            artist=album.artist,
            title=album.title,
            date=album.formatted_date(),
            tracks=album.formatted_tracks(),
            rating=rating,
            genres=album.formatted_genres(),
            tags=album.formatted_tags(),
            description=description)


def generate_items(items: List[Any]) -> str:
    item_template = Template("<span>$item</span>")
    return "\n".join(item_template.substitute(item=item) for item in items)


def saveTo(data: str, filename: str) -> None:
    Path(filename).write_text(data)


def save_album(album: Album, description: str, rating: str) -> None:
    Path("dist").mkdir(exist_ok=True)
    if album.cover_url:
        download_image(album.cover_url, "dist/cover.jpg")

    html = generate_html(
            album, 
            rating,
            description)
    saveTo(html, "dist/index.html")

if __name__ == "__main__":
    album = get_album("Shane Parish", "Repertoire")
    description = "Shane Parish's <em>Repertoire</em> is a stunning collection of reimagined classics, showcasing his virtuosic guitar work and unique interpretive style."
    rating = "★ ★ ★ ½"
    save_album(album, description, rating)
