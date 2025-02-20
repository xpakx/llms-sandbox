from pydantic import BaseModel
from album.model.track import Track
from typing import List, Optional, Any
from datetime import datetime
from string import Template


class Album(BaseModel):
    artist: str
    title: str
    date: str
    release_type: str
    label: str
    tracks: List[Track]
    genres: List[str]
    tags: List[str]
    cover_url: Optional[str]
    bandcamp_link: Optional[str] = None

    def formatted_date(self) -> str:
        date_obj = datetime.strptime(self.date, "%Y-%m-%d")
        return date_obj.strftime("%B %d, %Y")

    def formatted_tracks(self) -> str:
        return "".join(f"<li>{track.number}. {track.title} ({track.formatted_length()})</li>\n" for track in self.tracks)

    def formatted_tags(self) -> str:
       return generate_items(self.tags)

    def formatted_genres(self) -> str:
       return generate_items(self.genres)


def generate_items(items: List[Any]) -> str:
    item_template = Template("<span>$item</span>")
    return "\n".join(item_template.substitute(item=item) for item in items)
