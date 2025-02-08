from openai import OpenAI
import json
from typing import Generator, Dict, Any


def load_config(filename: str) -> Dict[str, Any]:
    with open(filename, 'r') as file:
        return json.load(file)


def get_client() -> OpenAI:
    config = load_config("config.json");
    url = "https://openrouter.ai/api/v1"
    return OpenAI(base_url=url, api_key=config["apiKey"])


def ask_deepseek(content: str) -> str:
    messages = [{"role": "user", "content": content}]
    try:
        completion = client.chat.completions.create(
                model="deepseek/deepseek-chat:free",
                messages=messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred while asking DeepSeek: {e}")
        raise

def stream_deepseek(client: OpenAI, content: str) -> Generator[str, None, None]:
    messages = [{"role": "user", "content": content}]
    try:
        completion = client.chat.completions.create(
            model="deepseek/deepseek-chat:free",
            messages=messages,
            stream=True
        )

        for chunk in completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        print(f"An error occurred while asking DeepSeek: {e}")
        raise

       
client = get_client()
print(ask_deepseek("Hello!"))

for chunk in stream_deepseek(client, "Hello from python!"):
    print(chunk, end="", flush=True)
