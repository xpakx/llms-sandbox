CREATE TABLE IF NOT EXISTS albums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    author TEXT NOT NULL,
    summary TEXT,
    uri TEXT NOT NULL,
    probability INTEGER
);

CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS album_genres (
    album_id INTEGER,
    genre_id INTEGER,
    FOREIGN KEY (album_id) REFERENCES albums(id),
    FOREIGN KEY (genre_id) REFERENCES genres(id),
    PRIMARY KEY (album_id, genre_id)
);

CREATE TABLE IF NOT EXISTS album_tags (
    album_id INTEGER,
    tag_id INTEGER,
    FOREIGN KEY (album_id) REFERENCES albums(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id),
    PRIMARY KEY (album_id, tag_id)
);

CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    rss_uri TEXT,
    title_selector TEXT NOT NULL,
    content_selector TEXT NOT NULL
);
