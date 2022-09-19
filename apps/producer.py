from json import dumps

import pika

from innotter.settings import RABBIT_QUEUE_NAME, RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_PORT, RABBITMQ_USER


def publish(method, body):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
    )
    channel = connection.channel()
    properties = pika.BasicProperties(method)
    channel.basic_publish(
        exchange="",
        routing_key=RABBIT_QUEUE_NAME,
        body=dumps(body),
        properties=properties,
    )
