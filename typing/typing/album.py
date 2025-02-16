import sqlite3


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


if __name__ == "__main__":
    conn = sqlite3.connect('albums.db')
    cursor = conn.cursor()

    execute_sql_file(cursor, "data.sql")
    conn.commit()

    show_tables(cursor)
    conn.close()
