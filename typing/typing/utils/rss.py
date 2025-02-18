import feedparser


def find_rss_link(html):
    try:
        rss_links = []
        for link in html.css('link'):
            if link.attributes.get('type') in ['application/rss+xml', 'application/atom+xml']:
                rss_links.append(link.attributes.get('href'))
        return rss_links[0] if rss_links else None
    except Exception as e:
        print(f"Error fetching or parsing: {e}")
        return None


def get_albums_rss(rss_url):
    if not rss_url:
        return [] # TODO
    feed = feedparser.parse(rss_url)
    return [entry.link for entry in feed.entries]
