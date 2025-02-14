from pydantic import BaseModel
from openai import OpenAI
from typing import Dict, Any
import json
from main import load_config, get_client, CssExtractionInfo
from scrapping import extract_content, get_page


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



if __name__ == "__main__":
    config = load_config("config.json")
    client = get_client(config["apiKey"])
    title_extractor = 'h3.post-title.entry-title'
    content_extractor='div.post-body.entry-content'
    css_dict = {'title': title_extractor, 'content': content_extractor}
    css = CssExtractionInfo(**css_dict)
    html = get_page("https://diskoryxeion.blogspot.com/2025/02/almufaraka.html")
    album = extract_content(html, css)
    event = album_evaluation(client, album['content'])
    print(event)
