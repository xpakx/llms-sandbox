import asyncio
from aioclock import Every
from aioclock.group import Group

from scheduler import get_scheduler


tasks = asyncio.Queue()
scheduler = Group()


@scheduler.task(trigger=Every(seconds=5))
async def test():
    print('test')


async def run(app):
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
