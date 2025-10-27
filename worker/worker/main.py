import asyncio

from aioclock import Every
from aioclock.group import Group
from worker.scheduler import get_scheduler
from worker.fibonacci import fibonacci_backoff

scheduler = Group()


tasks = asyncio.Queue(maxsize=3)


def my_task(t):
    async def task():
        print(f"Task start: {t}")
        await asyncio.sleep(2)
        print(f"Task end: {t}")
        if t == "HI":
            raise Exception(t)
        return True
    return task


@scheduler.task(trigger=Every(seconds=5))
async def main():
    if not tasks.empty():
        t = await tasks.get()
        task = my_task(t)
        result = await fibonacci_backoff(task, 5)
        print(f"Task returned {result}")
    else:
        print("No tasks")


async def feeder():
    for msg in ["HI", "HEY", "HELLO", "MORNING", "BYE"]:
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
    asyncio.run(main_entry(app))
