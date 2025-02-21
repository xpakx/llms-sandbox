from pathlib import Path
from album.model.album import Album
import requests
from string import Template


def save_to(data: str, filename: str) -> None:
    Path(filename).write_text(data)


def save_album(album: Album, description: str, rating: str) -> None:
    Path("dist").mkdir(exist_ok=True)
    if album.cover_url:
        download_image(album.cover_url, "dist/cover.jpg")

    html = generate_html(
            album, 
            rating,
            description)
    save_to(html, "dist/index.html")


def download_image(image_url: str, filename: str) -> None:
    response = requests.get(image_url)
    if response.status_code == 200:
        # TODO: resize if too big
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download image: {filename}")


def generate_html(album: Album, rating: str, description: str) -> str:
    with open('files/index.html', 'r') as file:
        content = file.read()
    template = Template(content)
    return template.substitute(
            artist=album.artist,
            title=album.title,
            date=album.formatted_date(),
            tracks=album.formatted_tracks(),
            rating=rating,
            genres=album.formatted_genres(),
            tags=album.formatted_tags(),
            description=description)
