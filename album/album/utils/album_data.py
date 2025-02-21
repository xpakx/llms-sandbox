import time
from typing import Optional

from album.web.mb import get_mb_album, search_albums_by_artist
from album.web.bandcamp import get_bandcamp_album
from album.web.spotify import get_spotify_album
from album.utils.files import save_album
from album.model.album import Album
from album.model.track import Track
from album.config import load_config
from album.web.reviews.extractor import get_quietus_extractor, get_klofmag_extractor


def get_albums(artist: str) -> None:
    albums = search_albums_by_artist(artist)
    for album in albums:
        print(album['title'])
        print(album['first-release-date'])
        print(album['id'])

def get_album(config, artist: str, name: str) -> Optional[Album]:
    # return get_mb_album(artist, name)
    # return get_bandcamp_album(artist, name)
    return get_spotify_album(config,artist, name)

if __name__ == "__main__":
    config = load_config("config.json")
    album = get_album(config, "Shane Parish", "Repertoire")
    if album:
        description = "Shane Parish's <em>Repertoire</em> is a stunning collection of reimagined classics, showcasing his virtuosic guitar work and unique interpretive style."
        rating = "★ ★ ★ ½"
        genres = ["american primitivism", "folk"]
        tags = ["fingerpicking", "solo guitar"]
        album.genres = genres
        album.tags = tags
        save_album(album, description, rating)
