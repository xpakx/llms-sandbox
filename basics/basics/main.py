from openai import OpenAI
import json
from typing import Generator, Dict, Any
import tempfile
import subprocess


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

       
def test(client: OpenAI):
    print(ask_deepseek("Hello!"))

    for chunk in stream_deepseek(client, "Hello from python!"):
        print(chunk, end="", flush=True)


def stream_chat(client: OpenAI, messages) -> Generator[str, None, None]:
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


def get_input(prompt="Enter message:"):
    query = input(prompt + " ")
    if query != "":
        return query
    with tempfile.NamedTemporaryFile(suffix=".txt", mode='w+') as temp_file:
        subprocess.call(['nvim', temp_file.name])
        temp_file.seek(0)
        user_input = temp_file.read().strip()
    return user_input


def chat(client: OpenAI):
    query: str = ""
    history = []
    response = ""
    while True:
        query = get_input()
        if query == "":
            break
        history.append({"role": "user", "content": query})
        response = ""
        for chunk in stream_chat(client, history):
            print(chunk, end="", flush=True)
            response += chunk
        print("\n");
        history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    client = get_client()
    chat(client)
