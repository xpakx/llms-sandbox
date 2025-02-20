from urllib.parse import quote
from selectolax.parser import HTMLParser
import requests
from typing import Optional
import time


class ReviewExtractor:
    def __init__(self, search_url_pattern: str, search_css: str, content_css: str):
        self.search_url_pattern = search_url_pattern
        self.search_css = search_css
        self.content_css = content_css
    
    def get_url(self, artist: str, title: str) -> str:
        query = quote(f"{artist} {title}")
        return self.search_url_pattern.format(query=query)

    def find_review(self, artist: str, title: str) -> Optional[str]:
        url = self.get_url(artist, title)
        response = requests.get(url)
        parser =  HTMLParser(response.text)
        results = parser.css(self.search_css)
        if len(results) == 0:
            return None
        attrs = results[0].attributes
        if 'href' in attrs:
            return attrs['href'].split('?')[0]

    def get_review(self, artist: str, title: str) -> Optional[str]:
        url = self.find_review(artist, title)
        print(url)
        if not url:
            return None
        time.sleep(1)
        response = requests.get(url)
        parser =  HTMLParser(response.text)
        result = parser.css_first(self.content_css)
        if not result:
            return None
        return result.text()


def get_quietus_extractor():
    return ReviewExtractor(
        search_url_pattern="https://thequietus.com/?s={query}&filter=reviews",
        search_css='div[class~="search-results--items"] a',
        content_css='div[class="entry-content"]'
    )


def get_klofmag_extractor():
    return ReviewExtractor(
        search_url_pattern="https://klofmag.com/?s={query}",
        search_css='div[id="main"] ul li a',
        content_css='div[class~="post-entry"]'
    )
