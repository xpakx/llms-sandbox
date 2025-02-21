import time
from typing import Optional

from album.web.mb import get_mb_album, search_albums_by_artist
from album.web.bandcamp import get_bandcamp_album
from album.web.spotify import get_spotify_album
from album.utils.files import save_album
from album.model.album import Album
from album.model.track import Track
from album.config import load_config, get_client, load_prompt
from album.web.reviews.extractor import get_quietus_extractor, get_klofmag_extractor
from album.ai.music import album_evaluation


def get_albums(artist: str) -> None:
    albums = search_albums_by_artist(artist)
    for album in albums:
        print(album['title'])
        print(album['first-release-date'])
        print(album['id'])


def get_album(config, artist: str, name: str) -> Optional[Album]:
    return get_mb_album(artist, name)
    # return get_bandcamp_album(artist, name)
    # return get_spotify_album(config, artist, name)

def generate_star_rating(score):
    score = (score / 100) * 9 + 1
    
    full_stars = int(score // 2)
    is_odd = int(score) % 2 != 0
    
    stars = "★ " * full_stars
    if is_odd:
        stars += "½"
    return stars


def get_reviews(artist: str, title: str):
    review_providers = [get_klofmag_extractor, get_quietus_extractor]
    taste = "experimental jazz, vocal experimentation, not too crazy about ambient"
    prompt = load_prompt("album_summary.md", taste=taste)

    for provider in review_providers:
        try:
            extractor = provider()
            review = extractor.get_review(artist, title)
            if review:
                evaluation = album_evaluation(client, review, prompt)
                if evaluation:
                    return evaluation
        except Exception as e:
            print(f"Evaluation not loaded: {e}")
            continue
    return None


if __name__ == "__main__":
    config = load_config("config.json")
    client = get_client(config["apiKey"])
    album = get_album(config, "Shane Parish", "Repertoire")
    evaluation = None
    if album:
        description = ""
        rating = ""
        evaluation = get_reviews("Shane Parish", "Repertoire")
        if evaluation:
            description = evaluation.summary
            album.genres = evaluation.genres
            album.tags = evaluation.tags
            rating = generate_star_rating(evaluation.probability)
        save_album(album, description, rating)
