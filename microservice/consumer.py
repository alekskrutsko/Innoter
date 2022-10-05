import json

from aio_pika import connect_robust
from aio_pika.abc import AbstractChannel, AbstractQueue

from microservice.services.page_service import (
    page_statistics_data,
    update_followers_counter,
    update_likes_counter,
    update_posts_counter,
)
from microservice.settings import settings


async def consume(loop):
    connection = await connect_robust(
        f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASS}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/",
        loop=loop,
    )

    async with connection:
        channel: AbstractChannel = await connection.channel()

        queue: AbstractQueue = await channel.declare_queue(
            settings.RABBIT_QUEUE_NAME,
        )

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    data = json.loads(message.body)

                    match message.properties.content_type.split("_")[0]:
                        case "like":
                            await update_likes_counter(
                                page_id=int(data),
                                field=message.properties.content_type,
                            ),
                        case "page":
                            await page_statistics_data(message.properties.content_type, data),
                        case "post":
                            await update_posts_counter(
                                page_id=int(data),
                                field=message.properties.content_type,
                            ),
                        case "follower":
                            await update_followers_counter(
                                page_id=int(data),
                                field=message.properties.content_type,
                            )

                    if queue.name in message.body.decode():
                        break
