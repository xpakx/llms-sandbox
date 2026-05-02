import asyncio
from aioclock import Every
from aioclock.group import Group
import msgspec
import requests

from scheduler import get_scheduler


class Data(msgspec.Struct):
    url: str


tasks = asyncio.Queue()
scheduler = Group()


async def add_task(data: str):
    try:
        config = msgspec.json.decode(data, type=Data)
        await tasks.put(config.url)
    except msgspec.DecodeError as e:
        print(f"Couldn't load config file {e}")


@scheduler.task(trigger=Every(seconds=5))
async def test():
    url = await tasks.get()
    response = requests.get(url)
    if response.status_code == 200:
        print(response.text)


async def run(app):
    await tasks.put("https://example.com")
    task = asyncio.create_task(app.serve())
    await task


def main():
    app = get_scheduler(scheduler)
    try:
        asyncio.run(run(app))
    except KeyboardInterrupt:
        print("Shutting down")


if __name__ == "__main__":
    main()
