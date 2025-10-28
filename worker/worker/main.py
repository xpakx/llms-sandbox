import asyncio

from aioclock import Every
from aioclock.group import Group
from pydantic import BaseModel
from worker.scheduler import get_scheduler
from worker.fibonacci import fibonacci_backoff
from worker.ai import AIWorker, get_client
from worker.prompt import Prompt
from worker.config import load_config
from worker.feeder import pika_feeder as feeder
from worker.publisher import pika_publisher as publisher


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
publish = None


def my_task(t):
    async def task():
        print(f"Task start: {t}")
        return ai.ask(t)
    return task


async def main_simple(message):
    task = my_task(message)
    result = await fibonacci_backoff(task, 5, start_index=4)
    print(f"Task returned {result}")


async def main_pika(message):
    t = message.body.decode()
    task = my_task(t)
    result = await fibonacci_backoff(task, 5, start_index=4)
    print(f"Task returned {result}")
    if result:
        try:
            await publish("joke", result.joke)
        except Exception as e:
            await message.nack(requeue=True)
            print(f"[Scheduler]  Error publishing {e}")
        else:
            await message.ack()
            print(f"[Scheduler] Acked message: {t}")
    else:
        await message.nack(requeue=True)
        print(f"[Scheduler]  Error processing {t}")


@scheduler.task(trigger=Every(seconds=5))
async def main():
    if not tasks.empty():
        message = await tasks.get()
        if type(message) is str:
            await main_simple(message)
        else:
            await main_pika(message)


async def main_entry(app):
    global publish
    publish, pub_connection = await publisher()
    scheduler_task = asyncio.create_task(app.serve())
    feeder_task = asyncio.create_task(feeder(tasks))

    await asyncio.gather(scheduler_task, feeder_task)
    await pub_connection.close()


if __name__ == "__main__":
    app = get_scheduler(scheduler)
    try:
        asyncio.run(main_entry(app))
    except KeyboardInterrupt:
        print("Shutting down by user request")
