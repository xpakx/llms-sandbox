from album.db.repo.tag import get_tag
from album.db.repo.genre import get_genre

def album_exists_by_url(cursor, url):
    cursor.execute("SELECT EXISTS(SELECT 1 FROM albums WHERE uri = ? LIMIT 1)", (url,))
    exists = cursor.fetchone()[0]
    return exists


def view_albums(cursor):
    query = '''
        SELECT name, author, summary, probability, uri
        FROM albums
    '''
    cursor.execute(query)
    result = cursor.fetchall()
    return result


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
