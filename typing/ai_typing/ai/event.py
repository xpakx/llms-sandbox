from pydantic import BaseModel
from openai import OpenAI
from datetime import datetime

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
