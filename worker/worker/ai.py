from pydantic import BaseModel
from worker.prompt import Prompt
from openai import OpenAI
from typing import Generic, TypeVar, Type


T = TypeVar("T", bound=BaseModel)


class AIWorker(Generic[T]):
    def __init__(
            self,
            client: OpenAI,
            model: str,
            prompt: Prompt,
            format: Type[T]
    ) -> None:
        self.client = client
        self.system_prompt = prompt
        self.model = model
        self.format = format

    def ask(self, message: str) -> T:
        try:
            completion = self.client.beta.chat.completions.parse(
                    model=self.model,
                    messages=self.prepare_message(message),
                    response_format=self.format
            )
            return completion.choices[0].message.parsed
        except Exception as e:
            print(f"An error occurred while asking AI: {e}")
            raise

    def prepare_message(self, message: str) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": self.prompt},
            {
                "role": "user",
                "content": message
            }
        ]

    def update_prompt(self, **kwargs: dict) -> None:
        self.prompt = self.system_prompt.compile(kwargs)


def get_client(api_key: str, provider: str) -> OpenAI:
    return OpenAI(base_url=provider, api_key=api_key)
