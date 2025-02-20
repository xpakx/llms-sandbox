import requests
from selectolax.parser import HTMLParser
from urllib.parse import quote


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
