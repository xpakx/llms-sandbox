import sqlite3

conn = sqlite3.connect('albums.db')
cursor = conn.cursor()

with open("data.sql", 'r') as file:
    sql_script = file.read()
cursor.executescript(sql_script)

conn.commit()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in the database:")
for table in tables:
    print(table[0])

conn.close()
