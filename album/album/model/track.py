from pydantic import BaseModel

class Track(BaseModel):
    number: str
    title: str
    length: int  # Length in milliseconds

    def formatted_length(self) -> str:
        minutes, seconds = divmod(self.length // 1000, 60)
        return f"{minutes:02d}:{seconds:02d}"
