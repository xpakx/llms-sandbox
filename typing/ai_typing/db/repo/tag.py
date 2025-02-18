def get_tag(cursor, name):
    cursor.execute(f'SELECT id FROM tags WHERE name = ?', (name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        cursor.execute(f'INSERT INTO tags (name) VALUES (?)', (name,))
        return cursor.lastrowid
