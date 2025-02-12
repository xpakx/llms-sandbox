from pydantic import BaseModel
from openai import OpenAI
from typing import Dict, Any
import json
from datetime import datetime

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
            {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."},
            ],
        response_format=CalendarEvent,
        )

event = completion.choices[0].message.parsed

print(event)

