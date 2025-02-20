from urllib.parse import urlparse, urlunparse

def parse_url(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        parsed = parsed._replace(scheme='https')
    return urlunparse(parsed)


def normalize_url(url):
    parsed = urlparse(url)
    normalized_url = urlunparse((parsed.scheme, parsed.netloc, '', '', '', ''))
    return normalized_url
