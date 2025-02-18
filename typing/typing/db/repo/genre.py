def get_genre(cursor, name):
    cursor.execute(f'SELECT id FROM genres WHERE name = ?', (name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute(f'INSERT INTO genres (name) VALUES (?)', (name,))
        return cursor.lastrowid
