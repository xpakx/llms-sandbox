from pydantic import BaseModel
from openai import OpenAI
from ai_typing.scrapping import fetch_skeleton_html


class CssExtractionInfo(BaseModel):
    title: str
    content: str


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
