from pydantic import BaseModel
from openai import OpenAI
from typing import Dict, Any
from datetime import datetime

from ai_typing.scrapping import fetch_skeleton_html, get_page, extract_content
from ai_typing.config import load_config, get_client
from ai_typing.ai.css import find_content, CssExtractionInfo


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]


def event_extraction(client: OpenAI, msg: str):
    prompt = """
             Extract the event information. Respond in valid JSON only. 
             Your response will be automatically validated, and shouldn't contain any tokens outside JSON object (e.g. no '```json' part).
             Format:  {"name": "name of event", "date": "01-20-1970", "participants": []}
             """

    completion = client.beta.chat.completions.parse(
            model="deepseek/deepseek-chat:free",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "system", "content": f"Today is {datetime.now()}"},
                {"role": "user", "content": msg},
                ],
            response_format=CalendarEvent,
            )

    return completion.choices[0].message.parsed


def extraction_example():
    config = load_config("config.json")
    client = get_client(config["apiKey"])
    # event = event_extraction(client, "Alice and Bob are going to a science fair on Friday.")
    html = get_page("https://aeon.co/essays/for-mary-midgley-philosophy-must-be-entangled-in-daily-life")
    data = find_content(client, html)
    print(data)
    event = extract_content(html, data)
    print(event)


def album_example():
    from ai_typing.ai.music import album_evaluation
    from ai_typing.scrapping import extract_content, get_page

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


if __name__ == "__main__":
    extraction_example()
    # album_example()
