from pydantic import BaseModel
from openai import OpenAI
from typing import Dict, Any
import json
from datetime import datetime
from scrapping import fetch_skeleton_html, get_page, extract_content

def load_config(filename: str) -> Dict[str, Any]:
    with open(filename, 'r') as file:
        return json.load(file)


def get_client(api_key: str) -> OpenAI:
    url = "https://openrouter.ai/api/v1"
    return OpenAI(base_url=url, api_key=api_key)

class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]


class CssExtractionInfo(BaseModel):
    title: str
    content: str


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
                {"role": "system", "content": f"Today is ${datetime.now()}"},
                {"role": "user", "content": msg},
                ],
            response_format=CalendarEvent,
            )

    return completion.choices[0].message.parsed


def find_content(client: OpenAI, url: str):
    skeleton = fetch_skeleton_html(url, ["#text", "#comment", "script", "style"])

    prompt = """
             Determine CSS extractor for selectolax for title and main content. Respond in valid JSON only. 
             Your response will be automatically validated, and shouldn't contain any tokens outside JSON object (e.g. no '```json' part).
             Format:  {"title": "css selector for title", "content": "css selector for content"}
             """
             
    completion = client.beta.chat.completions.parse(
            model="deepseek/deepseek-chat:free",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": skeleton},
                ],
            response_format=CssExtractionInfo,
            )

    return completion.choices[0].message.parsed

if __name__ == "__main__":
    config = load_config("config.json")
    client = get_client(config["apiKey"])
    # event = event_extraction(client, "Alice and Bob are going to a science fair on Friday.")
    html = get_page("https://aeon.co/essays/for-mary-midgley-philosophy-must-be-entangled-in-daily-life")
    data = find_content(client, html)
    print(data)
    event = extract_content(html, data)
    print(event)
