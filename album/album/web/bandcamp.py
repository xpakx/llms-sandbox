import requests
from selectolax.parser import HTMLParser
from urllib.parse import quote
from typing import Dict, Any
import json
import re

from album.model.track import Track
from album.model.album import Album


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


def get_bandcamp_data(link: str) -> Dict[str, Any]:
    response = requests.get(link)
    parser =  HTMLParser(response.text)
    result = parser.css_first('script[type="application/ld+json"]')
    data = json.loads(result.text())
    tracks_data = data['track']['itemListElement']

    tracks = [
        Track(
            number=track['position'],
            title=track['item']['name'],
            length=iso8601_duration_to_milliseconds(track['item']['duration']))
        for track in tracks_data if track['@type'] == 'ListItem'
    ]
    print(tracks)
    print(data['datePublished'])
    print(data['description'])
    print(data['creditText'])

    return {}


def iso8601_duration_to_milliseconds(duration):
    pattern = re.compile(r'P(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?')
    match = pattern.match(duration)
    
    if not match:
        raise ValueError("Invalid ISO 8601 duration format")
    
    hours = int(match.group('hours') or 0)
    minutes = int(match.group('minutes') or 0)
    seconds = int(match.group('seconds') or 0)
    
    total_milliseconds = (hours * 3600 + minutes * 60 + seconds) * 1000
    
    return total_milliseconds
