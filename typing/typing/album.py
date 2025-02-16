import sqlite3
import argparse
from main import load_config, get_client, find_content
from scrapping import get_page
from urllib.parse import urlparse, urlunparse


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
            print(rss)


def check_urls(cursor):
    print("Checking all URLs in the database")


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
    elif args.command == "view":
        view(cursor)
    else:
        parser.print_help()

    conn.close()
