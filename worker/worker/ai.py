from pydantic import BaseModel
from worker.prompt import Prompt
from openai import OpenAI


class Joke(BaseModel):
    genre: str
    joke: str
    evaluation: int
    tags: list[str]


class AIWorker:
    def __init__(
            self,
            client: OpenAI,
            model: str,
            prompt: Prompt,
    ) -> None:
        self.client = client
        self.system_prompt = prompt
        self.model = model

    def ask(self, message: str) -> Joke:
        try:
            completion = self.client.beta.chat.completions.parse(
                    model=self.model,
                    messages=self.prepare_message(message),
                    response_format=Joke
            )
            print(completion.choices[0].message.parsed)
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
