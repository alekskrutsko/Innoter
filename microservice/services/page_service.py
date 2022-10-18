from enum import Enum

import aioboto3
import botocore.exceptions
from boto3.dynamodb.conditions import Attr, Key

from microservice.models.page_statistics import Page
from microservice.settings import settings


class CommandTypes(str, Enum):
    CREATE_PAGE = "page_created"
    UPDATE_PAGE = "page_updated"
    DELETE_PAGE = "page_deleted"

    CREATE_POST = "post_created"
    DELETE_POST = "post_deleted"

    CREATE_LIKE = "like_created"
    DELETE_LIKE = "like_deleted"

    ADD_FOLLOWER = "follower_added"
    DELETE_FOLLOWER = "follower_deleted"
    ADD_ALL_FOLLOWERS = "follower_added_all"


async def create_table():
    session = aioboto3.Session()
    async with session.resource(
        "dynamodb",
        endpoint_url=settings.AWS_URL,
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    ) as dynamodb:
        try:
            await dynamodb.create_table(
                TableName=settings.AWS_DYNAMODB_TABLE_NAME,
                KeySchema=[
                    {'AttributeName': 'page_id', 'KeyType': 'HASH'},
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'page_id', 'AttributeType': 'N'},
                ],
                ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10},
            )
        except botocore.exceptions.ClientError:
            pass


async def page_statistics_data(content_type: str, data):
    match content_type:
        case CommandTypes.CREATE_PAGE:
            await create_new_page(Page.parse_obj(data))
        case CommandTypes.UPDATE_PAGE:
            await update_page(Page.parse_obj(data))
        case CommandTypes.DELETE_PAGE:
            await delete_page(int(data))


async def create_new_page(page):
    session = aioboto3.Session()
    async with session.resource(
        "dynamodb",
        endpoint_url=settings.AWS_URL,
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    ) as dynamo_resource:
        table = await dynamo_resource.Table(settings.AWS_DYNAMODB_TABLE_NAME)
        await table.put_item(
            Item={
                "page_id": page.id,
                "user_id": page.owner,
                "name": page.name,
                "description": page.description,
                "counters": {"amount_of_posts": 0, "amount_of_likes": 0, "amount_of_followers": 0},
            }
        )


async def update_page(page):
    session = aioboto3.Session()
    async with session.resource(
        "dynamodb",
        endpoint_url=settings.AWS_URL,
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    ) as dynamo_resource:
        table = await dynamo_resource.Table(settings.AWS_DYNAMODB_TABLE_NAME)
        table.update_item(
            Key={'page_id': page.id},
            UpdateExpression="SET name = :n, description = :d",
            ExpressionAttributeValues={":n": page.name, ":d": page.description},
        )


async def delete_page(page_id):
    session = aioboto3.Session()
    async with session.resource(
        "dynamodb",
        endpoint_url=settings.AWS_URL,
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    ) as dynamo_resource:
        table = await dynamo_resource.Table(settings.AWS_DYNAMODB_TABLE_NAME)
        table.delete_item(Key={'page_id': page_id})


async def update_posts_counter(page_id: int, field):
    match field:
        case CommandTypes.CREATE_POST:
            await update_page_statistics(page_id, 'amount_of_posts')
        case CommandTypes.DELETE_POST:
            await update_page_statistics(page_id, 'amount_of_posts', False)


async def update_likes_counter(page_id: int, field):
    match field:
        case CommandTypes.CREATE_LIKE:
            await update_page_statistics(page_id, 'amount_of_likes')
        case CommandTypes.DELETE_LIKE:
            await update_page_statistics(page_id, 'amount_of_likes', False)


async def update_followers_counter(data, field):
    match field:
        case CommandTypes.ADD_FOLLOWER:
            await update_page_statistics(int(data), 'amount_of_followers')
        case CommandTypes.ADD_ALL_FOLLOWERS:
            await update_page_statistics(int(data['page_id']), 'amount_of_followers', True, int(data["quantity"]))
        case CommandTypes.DELETE_FOLLOWER:
            await update_page_statistics(int(data), 'amount_of_followers', False)


async def update_page_statistics(page_id: int, value, increase=True, quantity: int = 0):
    session = aioboto3.Session()
    async with session.resource(
        "dynamodb",
        endpoint_url=settings.AWS_URL,
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    ) as dynamo_resource:
        table = await dynamo_resource.Table(settings.AWS_DYNAMODB_TABLE_NAME)
        if quantity == 0:
            number = 1
        else:
            number = quantity
        await table.update_item(
            Key={'page_id': page_id},
            UpdateExpression=f"ADD counters.{value} :value",
            ExpressionAttributeValues={":value": number if increase else -1},
        )


async def retrieve_pages_statistics(user_id, page_id=None):
    session = aioboto3.Session()
    async with session.resource(
        "dynamodb",
        endpoint_url=settings.AWS_URL,
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    ) as dynamo_resource:
        table = await dynamo_resource.Table(settings.AWS_DYNAMODB_TABLE_NAME)
        if not page_id:
            return await table.scan(FilterExpression=Attr("user_id").eq(user_id))
        response = await table.query(
            KeyConditionExpression=Key('page_id').eq(page_id), FilterExpression=Attr('user_id').eq(user_id)
        )
        if not response['Items']:
            return 404
        return response
