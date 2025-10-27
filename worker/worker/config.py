from pydantic import BaseModel
import json


class Config(BaseModel):
    api_key: str
    provider: str
    model: str


def load_config(filename: str) -> Config:
    with open(filename, 'r') as file:
        data = json.load(file)
    return Config(**data)
