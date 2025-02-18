from pydantic import BaseModel
from openai import OpenAI
from typing import Dict, Any
from datetime import datetime

from ai_typing.scrapping import fetch_skeleton_html, get_page, extract_content
from ai_typing.config import load_config, get_client, load_prompt
from ai_typing.ai.css import find_content, CssExtractionInfo
from ai_typing.ai.event import event_extraction


def event_example():
    config = load_config("config.json")
    client = get_client(config["apiKey"])
    event = event_extraction(client, "Alice and Bob are going to a science fair on Friday.")
    print(event)


def extraction_example():
    css_prompt = load_prompt("css_extractors.md")

    config = load_config("config.json")
    client = get_client(config["apiKey"])
    html = get_page("https://aeon.co/essays/for-mary-midgley-philosophy-must-be-entangled-in-daily-life")
    data = find_content(client, html, css_prompt)
    print(data)
    event = extract_content(html, data)
    print(event)


def album_example():
    from ai_typing.ai.music import album_evaluation
    from ai_typing.scrapping import extract_content, get_page

    taste = "avant-pop with folk undertones."
    prompt = load_prompt("album_evaluation.md", taste=taste)

    config = load_config("config.json")
    client = get_client(config["apiKey"])
    title_extractor = 'h3.post-title.entry-title'
    content_extractor='div.post-body.entry-content'
    css_dict = {'title': title_extractor, 'content': content_extractor}
    css = CssExtractionInfo(**css_dict)
    html = get_page("https://diskoryxeion.blogspot.com/2025/02/almufaraka.html")
    album = extract_content(html, css)
    event = album_evaluation(client, album['content'], prompt)
    print(event)


if __name__ == "__main__":
    event_example()
    # extraction_example()
    # album_example()
