import asyncio
from aioclock import Every
from aioclock.group import Group
import msgspec
from httpx import AsyncClient

from scheduler import get_scheduler


class Task(msgspec.Struct):
    id: str
    url: str


class TaskResponse(msgspec.Struct):
    id: str
    url: str
    content: str


fetch_tasks = asyncio.Queue()
scheduler = Group()
requests = AsyncClient()


async def add_task(data: str):
    try:
        task = msgspec.json.decode(data, type=Task)
        await fetch_tasks.put(task)
    except msgspec.DecodeError as e:
        print(f"Couldn't load config file {e}")


@scheduler.task(trigger=Every(seconds=5))
async def fetch():
    task = await fetch_tasks.get()
    response = await requests.get(task.url)
    if response.status_code == 200:
        task_response = TaskResponse(
                id=task.id,
                url=task.url,
                content=response.text,
        )
        formatted_json = msgspec.json.encode(task_response)
        print(formatted_json)


async def run(app):
    await add_task('{"url": "https://example.com", "id": "aaa"}')
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
