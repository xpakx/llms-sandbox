from openai import OpenAI
from typing import Dict, Any
import json
from string import Template


def load_config(filename: str) -> Dict[str, Any]:
    with open(filename, 'r') as file:
        return json.load(file)


def get_client(api_key: str) -> OpenAI:
    url = "https://openrouter.ai/api/v1"
    return OpenAI(base_url=url, api_key=api_key)


def load_prompt(filename: str, **kwargs) -> str:
    with open(f'prompts/{filename}', 'r') as file:
        content = file.read()
    if len(kwargs) == 0:
        return content
    template = Template(content)
    return template.substitute(**kwargs)
