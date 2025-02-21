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
        possible_formats = ["%Y-%m-%d", "%Y-%m", "%Y", "%d %b %Y %H:%M:%S %Z"]
        
        for fmt in possible_formats:
            try:
                date_obj = datetime.strptime(self.date, fmt)
                if fmt == "%Y-%m":
                    return date_obj.strftime("%B %Y")
                elif fmt == "%Y":
                    return date_obj.strftime("%Y")
                else:
                    return date_obj.strftime("%B %d, %Y")
            except ValueError:
                continue
        return self.date

    def formatted_tracks(self) -> str:
        return "".join(f"<li>{track.number}. {track.title} ({track.formatted_length()})</li>\n" for track in self.tracks)

    def formatted_tags(self) -> str:
       return generate_items(self.tags)

    def formatted_genres(self) -> str:
       return generate_items(self.genres)


def generate_items(items: List[Any]) -> str:
    item_template = Template("<span>$item</span>")
    return "\n".join(item_template.substitute(item=item) for item in items)
