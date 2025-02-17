import sqlite3
import argparse
from main import load_config, get_client, find_content, CssExtractionInfo
from scrapping import get_page, extract_content
from urllib.parse import urlparse, urlunparse, urljoin
import feedparser
import time
from music import album_evaluation


def execute_sql_file(cursor, sql_file):
    with open(sql_file, 'r') as file:
        sql_script = file.read()
    cursor.executescript(sql_script)


def show_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(table[0])


def get_parser():
    parser = argparse.ArgumentParser(description="A program to manage albums.")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    parser_url = subparsers.add_parser("url", help="Manage URLs")
    url_subparsers = parser_url.add_subparsers(dest="subcommand", help="Available subcommands")
    parser_url_add = url_subparsers.add_parser("add", help="Add a new URL to track")
    parser_url_add.add_argument("url", type=str, help="The URL to add")

    parser_check = subparsers.add_parser("check", help="Check all URLs in the database for new albums")
    parser_view = subparsers.add_parser("view", help="Print all albums in the database")
    return parser


def get_selectors_by_url(cursor, url):
    query = '''
        SELECT title_selector, content_selector
        FROM sites
        WHERE uri = ?
    '''
    cursor.execute(query, (url,))
    result = cursor.fetchone()
    if result:
        title_selector, content_selector = result
        return title_selector, content_selector
    else:
        return None, None


def parse_url(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        parsed = parsed._replace(scheme='https')
    return urlunparse(parsed)


def normalize_url(url):
    parsed = urlparse(url)
    normalized_url = urlunparse((parsed.scheme, parsed.netloc, '', '', '', ''))
    return normalized_url


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


def add_url_to_db(cursor, url, rss_uri, title_selector, content_selector):
    cursor.execute('''
        INSERT INTO sites (uri, rss_uri, title_selector, content_selector)
        VALUES (?, ?, ?, ?)
    ''', (url, rss_uri, title_selector, content_selector))


def add_url(cursor, client, url):
    print(f"Adding URL: {args.url}")
    url = parse_url(url)
    main_url = normalize_url(url)
    title_selector, content_selector = get_selectors_by_url(cursor, main_url)

    if title_selector and content_selector:
        print("Already added!")
        print(f"Title Selector: {title_selector}")
        print(f"Content Selector: {content_selector}")
    else:
        print(f"No selectors found for URL: {url}")
        print(main_url)
        html = get_page(url)
        data = find_content(client, html)
        if not data:
            print("Couldn't find selectors.")
            return
        print(data)

        rss = find_rss_link(html)
        if not rss:
            print("No RSS feed!")
        else:
            rss = urljoin(main_url, rss)
            print(rss)
        add_url_to_db(cursor, main_url, rss, data.title, data.content)


def get_sites(cursor):
    query = '''
        SELECT id, uri, rss_uri, title_selector, content_selector
        FROM sites
    '''
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def get_albums(rss_url):
    if not rss_url:
        return [] # TODO
    feed = feedparser.parse(rss_url)
    return [entry.link for entry in feed.entries]


def check_urls(cursor):
    print("Checking all URLs in the database")
    sites = get_sites(cursor)
    print(sites)
    if not sites:
        print("No URLs in the database.")
        return
    for site in sites:
        print(site[1])
        albums = get_albums(site[2])
        for album in albums:
            if album_exists_by_url(cursor, album):
                continue
            time.sleep(1)
            html = get_page(album)
            extr = {"title": site[3], "content": site[4]}
            css = CssExtractionInfo(**extr)
            event = extract_content(html, css)
            try:
                evaluation = album_evaluation(client, f"<h1>{event['title']}</h1> {event['content']}")
                if not evaluation:
                    continue
            except Exception as e:
                continue
            save_album(cursor, evaluation, album)


def get_tag(cursor, name):
    cursor.execute(f'SELECT id FROM tags WHERE name = ?', (name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute(f'INSERT INTO tags (name) VALUES (?)', (name,))
        return cursor.lastrowid


def get_genre(cursor, name):
    cursor.execute(f'SELECT id FROM genres WHERE name = ?', (name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute(f'INSERT INTO genres (name) VALUES (?)', (name,))
        return cursor.lastrowid


def save_album(cursor, album, uri):
    if not album:
        return
    print(album)
    cursor.execute('''
        INSERT INTO albums (name, author, summary, uri, probability)
        VALUES (?, ?, ?, ?, ?)
    ''', (album.name, album.author, album.summary, uri, album.probability))
    album_id = cursor.lastrowid

    for genre_name in album.genres:
        genre_id = get_genre(cursor, genre_name)
        cursor.execute('INSERT INTO album_genres (album_id, genre_id) VALUES (?, ?)', (album_id, genre_id))

    for tag_name in album.tags:
        tag_id = get_tag(cursor, tag_name)
        cursor.execute('INSERT INTO album_tags (album_id, tag_id) VALUES (?, ?)', (album_id, tag_id))


def album_exists_by_url(cursor, url):
    cursor.execute("SELECT EXISTS(SELECT 1 FROM albums WHERE uri = ? LIMIT 1)", (url,))
    exists = cursor.fetchone()[0]
    return exists


def view(cursor):
    print("Viewing all data in the database")


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    conn = sqlite3.connect('albums.db')
    cursor = conn.cursor()
    execute_sql_file(cursor, "data.sql")
    conn.commit()
    # show_tables(cursor)
    config = load_config("config.json")
    client = get_client(config["apiKey"])

    if args.command == "url" and args.subcommand == "add":
        add_url(cursor, client, args.url)
        conn.commit()
    elif args.command == "check" or args.command == None:
        check_urls(cursor)
        conn.commit()
    elif args.command == "view":
        view(cursor)
    else:
        parser.print_help()

    conn.close()
