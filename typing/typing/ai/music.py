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


def album_evaluation(client: OpenAI, msg: str):
    prompt = """
             Extract and evaluate the album information. Respond in valid JSON only. 
             Your response will be automatically validated and shouldn't contain any tokens outside JSON object (e.g. no '```json' part).
             `probability` is the probability of the user liking the album. `summary` is an explanation of this rating. genres and tags should be list of strings
             Format:  {"name": "name of album", "author": "name of author", "probability": 10, "summary": "one sentence of explanation", "genres": [], "tags": ""}
             """

    taste = "experimental jazz, vocal experimentation, not too crazy about ambient"

    completion = client.beta.chat.completions.parse(
            model="deepseek/deepseek-chat:free",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "system", "content": f"user taste: {taste}"},
                {"role": "user", "content": msg},
                ],
            response_format=AlbumEvaluation,
            )

    return completion.choices[0].message.parsed
