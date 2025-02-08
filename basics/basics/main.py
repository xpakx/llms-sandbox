from openai import OpenAI
import json


def load_config(filename: str):
    with open(filename, 'r') as file:
        return json.load(file)


def get_client():
    config = load_config("config.json");
    url = "https://openrouter.ai/api/v1"
    return OpenAI(base_url=url, api_key=config["apiKey"])


def ask_deepseek(content: str):
    messages = [{"role": "user", "content": content}]
    completion = client.chat.completions.create(
            model="deepseek/deepseek-chat:free",
            messages=messages
    )
    return completion.choices[0].message.content

       
client = get_client()
print(ask_deepseek("Hello!"))
