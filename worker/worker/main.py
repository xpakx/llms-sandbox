import asyncio

from aioclock import Every
from aioclock.group import Group
from pydantic import BaseModel
from worker.scheduler import get_scheduler
from worker.fibonacci import fibonacci_backoff
from worker.ai import AIWorker, get_client
from worker.prompt import Prompt
from worker.config import load_config


class Joke(BaseModel):
    genre: str
    joke: str
    evaluation: int
    tags: list[str]


scheduler = Group()


config = load_config("files/config.json")
client = get_client(config.api_key, config.provider)
tasks = asyncio.Queue(maxsize=3)
prompt = Prompt("joke.md")
ai = AIWorker(client, config.model, prompt, Joke)
ai.update_prompt()


def my_task(t):
    async def task():
        print(f"Task start: {t}")
        return ai.ask(t)
    return task


@scheduler.task(trigger=Every(seconds=5))
async def main():
    if not tasks.empty():
        t = await tasks.get()
        task = my_task(t)
        result = await fibonacci_backoff(task, 5, start_index=4)
        print(f"Task returned {result}")
    else:
        print("No tasks")


async def feeder():
    for msg in ["Joke about birds", "Joke about computers", "Tell me a joke"]:
        await asyncio.sleep(1)
        await tasks.put(msg)
        print(f"[+] Added task: {msg}")
    print("[!] No more tasks to add.")


async def main_entry(app):
    scheduler_task = asyncio.create_task(app.serve())
    feeder_task = asyncio.create_task(feeder())

    await asyncio.gather(scheduler_task, feeder_task)


if __name__ == "__main__":
    app = get_scheduler(scheduler)
    try:
        asyncio.run(main_entry(app))
    except KeyboardInterrupt:
        print("Shutting down by user request")
