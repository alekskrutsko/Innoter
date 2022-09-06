import boto3
from celery import shared_task

from innotter import settings


@shared_task
def notify_follower_about_new_post(post_owner, post_content, followers_list):
    ses = boto3.client(
        "ses",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION,
    )
    ses.send_email(
        Destination={
            'ToAddresses': [followers_list],
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': post_content,
                },
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': f'{post_owner} has published a new post',
            },
        },
        Source=settings.DEFAULT_FROM_EMAIL,
    )
