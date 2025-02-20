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


def add_url_to_db(cursor, url, rss_uri, title_selector, content_selector):
    cursor.execute('''
        INSERT INTO sites (uri, rss_uri, title_selector, content_selector)
        VALUES (?, ?, ?, ?)
    ''', (url, rss_uri, title_selector, content_selector))


def get_sites(cursor):
    query = '''
        SELECT id, uri, rss_uri, title_selector, content_selector
        FROM sites
    '''
    cursor.execute(query)
    result = cursor.fetchall()
    return result
