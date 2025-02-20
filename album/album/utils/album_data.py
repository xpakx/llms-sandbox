import time
from typing import Optional
from album.web.mb import search_albums_by_artist, get_album_cover, search_album, get_tracks
from album.web.bandcamp import find_bandcamp_link
from album.utils.files import save_album
from album.model.album import Album
from album.model.track import Track


def get_album(artist: str, title: str) -> Optional[Album]:
    print(f"Fetching album: {artist} - {title}.")
    album = search_album(artist, title)

    if album and album['id']:
        date = album['date']
        release_type = album['release-group']['primary-type'] if 'primary-type' in album['release-group'] else ""
        label = album['label-info'][0]['label']['name']

        time.sleep(1)
        tracks_data = get_tracks(album['id'])
        tracks = [
            Track(number=track['number'], title=track['title'], length=track['length'])
            for track in tracks_data['tracks']
        ]
    else:
        print("Album not found in MusicBrainz")
        return None

    bandcamp_link = find_bandcamp_link(artist, title)

    time.sleep(1)
    cover = get_album_cover(album['id'])

    return Album(
        title=title,
        artist=artist,
        date=date,
        release_type=release_type,
        label=label,
        tracks=tracks,
        genres=["american primitivism", "folk"],
        tags=["fingerpicking", "solo guitar"],
        cover_url=cover,
        bandcamp_link=bandcamp_link
    )


def get_albums(artist: str) -> None:
    albums = search_albums_by_artist(artist)
    for album in albums:
        print(album['title'])
        print(album['first-release-date'])
        print(album['id'])


if __name__ == "__main__":
    album = get_album("Shane Parish", "Repertoire")
    description = "Shane Parish's <em>Repertoire</em> is a stunning collection of reimagined classics, showcasing his virtuosic guitar work and unique interpretive style."
    rating = "★ ★ ★ ½"
    save_album(album, description, rating)
