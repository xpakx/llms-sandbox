import sqlite3
from urllib.parse import urljoin
import time

from ai_typing.ai.css import find_content, CssExtractionInfo
from ai_typing.ai.music import album_evaluation
from ai_typing.config import load_config, get_client, load_prompt
from ai_typing.db.utils import execute_sql_file, show_tables
from ai_typing.db.repo.site import get_selectors_by_url, add_url_to_db, get_sites
from ai_typing.db.repo.album import save_album, view_albums, album_exists_by_url
from ai_typing.scrapping import get_page, extract_content
from ai_typing.utils.url import parse_url, normalize_url
from ai_typing.utils.console import get_parser
from ai_typing.utils.rss import find_rss_link, get_albums_rss


def add_url(cursor, client, url, prompt):
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
        data = find_content(client, html, prompt)
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


def check_urls(cursor, prompt):
    print("Checking all URLs in the database")
    sites = get_sites(cursor)
    print(sites)
    if not sites:
        print("No URLs in the database.")
        return
    for site in sites:
        print(site[1])
        albums = get_albums_rss(site[2])
        for album in albums:
            if album_exists_by_url(cursor, album):
                continue
            time.sleep(1)
            html = get_page(album)
            extr = {"title": site[3], "content": site[4]}
            css = CssExtractionInfo(**extr)
            event = extract_content(html, css)
            try:
                evaluation = album_evaluation(client, f"<h1>{event['title']}</h1> {event['content']}", prompt)
                if not evaluation:
                    continue
            except Exception as e:
                continue
            save_album(cursor, evaluation, album)


def view(cursor):
    print("Viewing all data in the database")
    print(view_albums(cursor))


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    taste = "experimental jazz, vocal experimentation, not too crazy about ambient"
    prompt = load_prompt("album_evaluation.md", taste=taste)
    css_prompt = load_prompt("css_extractors.md")

    conn = sqlite3.connect('albums.db')
    cursor = conn.cursor()
    execute_sql_file(cursor, "data.sql")
    conn.commit()
    # show_tables(cursor)
    config = load_config("config.json")
    client = get_client(config["apiKey"])

    if args.command == "url" and args.subcommand == "add":
        add_url(cursor, client, args.url, css_prompt)
        conn.commit()
    elif args.command == "check" or args.command == None:
        check_urls(cursor, prompt)
        conn.commit()
    elif args.command == "view":
        view(cursor)
    else:
        parser.print_help()

    conn.close()
