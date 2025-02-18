from openai import OpenAI
from typing import Dict, Any
import json


def load_config(filename: str) -> Dict[str, Any]:
    with open(filename, 'r') as file:
        return json.load(file)


def get_client(api_key: str) -> OpenAI:
    url = "https://openrouter.ai/api/v1"
    return OpenAI(base_url=url, api_key=api_key)
