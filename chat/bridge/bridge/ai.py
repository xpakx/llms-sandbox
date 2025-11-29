from openai import OpenAI
from typing import Generator, Any


def get_client(api_key: str, provider: str) -> OpenAI:
    return OpenAI(base_url=provider, api_key=api_key)


def ask_deepseek(client: OpenAI, messages: Any) -> str:
    try:
        completion = client.chat.completions.create(
                model="gemini-2.5-flash-lite",
                messages=messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred while asking DeepSeek: {e}")
        raise


def stream_deepseek(client: OpenAI, messages: Any) -> Generator[str, None, None]:
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


