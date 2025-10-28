import aio_pika


RABBITMQ_URL = "amqp://guest:guest@localhost/"
EXCHANGE_NAME = "jokes.topic"


async def pika_publisher():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    exchange = await channel.declare_exchange(
        EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
    )

    async def publish(routing_key: str, message: str):
        await exchange.publish(
            aio_pika.Message(
                body=message.encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )
        print(f"[Publisher] Sent '{routing_key}': {message}")

    return publish, connection
