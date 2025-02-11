from pydantic import BaseModel
from openai import OpenAI
from typing import Dict, Any
import json

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

config = load_config("config.json")
client = get_client(config["apiKey"])

completion = client.beta.chat.completions.parse(
        model="deepseek/deepseek-chat:free",
        messages=[
            {"role": "system", "content": "Extract the event information."},
            {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."},
            ],
        response_format=CalendarEvent,
        )

event = completion.choices[0].message.parsed

print(event)

