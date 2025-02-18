from pydantic import BaseModel
from openai import OpenAI
from ai_typing.scrapping import fetch_skeleton_html


class CssExtractionInfo(BaseModel):
    title: str
    content: str


def find_content(client: OpenAI, url: str, prompt):
    skeleton = fetch_skeleton_html(url, ["#text", "#comment", "script", "style"])

    completion = client.beta.chat.completions.parse(
            model="deepseek/deepseek-chat:free",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": skeleton},
                ],
            response_format=CssExtractionInfo,
            )

    return completion.choices[0].message.parsed
