from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from aioclock import AioClock
from aioclock.group import Group


@asynccontextmanager
async def lifespan(aio_clock: AioClock) -> AsyncGenerator[AioClock]:
    print("Scheduler started")
    yield aio_clock
    print("Going offline.")


def get_scheduler(group: Group) -> AioClock:
    app = AioClock(lifespan=lifespan)
    app.include_group(group)
    return app
