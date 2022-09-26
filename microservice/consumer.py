import json

import pika

from microservice.services.page_service import (
    page_statistics_data,
    update_followers_counter,
    update_likes_counter,
    update_posts_counter,
)
from microservice.settings import settings

credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT, credentials=credentials)
)
channel = connection.channel()
channel.queue_declare(queue=settings.RABBIT_QUEUE_NAME)


async def callback(ch, method, properties, body):
    data = json.loads(body)

    match properties.content_type.split("_")[0]:
        case "like":
            await update_likes_counter(
                page_id=data['id'],
                field=properties.content_type,
            ),
        case "page":
            await page_statistics_data(properties.content_type, data),
        case "post":
            await update_posts_counter(
                page_id=data['id'],
                field=properties.content_type,
            ),
        case "follower":
            await update_followers_counter(
                page_id=data['id'],
                field=properties.content_type,
            )


channel.basic_consume(queue=settings.RABBIT_QUEUE_NAME, on_message_callback=callback, auto_ack=True)

channel.start_consuming()

channel.close()
