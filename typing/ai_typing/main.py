from pydantic import BaseModel
from openai import OpenAI
from typing import Dict, Any
from datetime import datetime

from scrapping import fetch_skeleton_html, get_page, extract_content
from config import load_config, get_client, load_prompt
from ai.css import find_content, CssExtractionInfo
from ai.event import event_extraction


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

    skeleton = fetch_skeleton_html(html, ["#text", "#comment", "script", "style"])
    data = find_content(client, html, css_prompt, skeleton)
    print(data)
    event = extract_content(html, data)
    print(event)


if __name__ == "__main__":
    event_example()
    # extraction_example()
