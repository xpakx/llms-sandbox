from pydantic import BaseModel
from openai import OpenAI
from typing import Dict, Any
import json


class AlbumEvaluation(BaseModel):
    name: str
    author: str
    summary: str
    probability: int
    genres: list[str]
    tags: list[str]


def album_evaluation(client: OpenAI, msg: str, prompt: str):
    completion = client.beta.chat.completions.parse(
            model="deepseek/deepseek-chat:free",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": msg},
                ],
            response_format=AlbumEvaluation,
            )

    return completion.choices[0].message.parsed
