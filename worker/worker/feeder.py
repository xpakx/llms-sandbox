import asyncio
import aio_pika


async def test_feeder(tasks: asyncio.Queue):
    for msg in ["Joke about birds", "Joke about computers", "Tell me a joke"]:
        await asyncio.sleep(1)
        await tasks.put(msg)
        print(f"[+] Added task: {msg}")
    print("[!] No more tasks to add.")

RABBITMQ_URL = "amqp://guest:guest@localhost/"
EXCHANGE_NAME = "jokes.topic"
QUEUE_NAME = "jokes.requests.queue"


async def pika_feeder(tasks: asyncio.Queue):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
    )

    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.bind(exchange, routing_key="request")

    print("[Feeder] Subscribed to queue:", QUEUE_NAME)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            await tasks.put(message)
            print(f"[Feeder] Queued message: {message.body.decode()}")

    await connection.close()
