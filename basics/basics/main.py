from openai import OpenAI
import json
from typing import Generator, Dict, Any
import tempfile
import subprocess
import os


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

    editor = os.environ.get("EDITOR", "nvim")

    if query != "":
        return query
    with tempfile.NamedTemporaryFile(suffix=".txt", mode='w+', delete=False) as temp_file:
        temp_file_path = temp_file.name

    while True:
        subprocess.call([editor, temp_file_path])
        with open(temp_file_path, 'r') as temp_file:
            user_input = temp_file.read().strip()

        print("\nOptions:")
        print("[e] Continue editing")
        print("[] Send this message")
        choice = input("Choose an option: ").strip()

        if choice == 'w':
            continue 
        else:
            return user_input



def chat(client: OpenAI):
    query: str = ""
    history = [{"role": "system", "content": "Respond with brief, conversational messages. Keep it concise and to the point."}]
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
