from microservice.models.page_statistics import Page
from microservice.services.database_service import table


async def page_statistics_data(content_type: str, data):
    match content_type:
        case "page_created":
            await create_new_page(Page.parse_obj(data))
        case "page_updated":
            await update_page(Page.parse_obj(data))
        case "page_deleted":
            await delete_page(data["id"])


async def create_new_page(page):
    table.put_item(
        Item={
            "id": page.id,
            "user_id": page.owner,
            "name": page.name,
            "description": page.description,
            "counters": {"amount_of_posts": 0, "amount_of_likes": 0, "amount_of_followers": 0},
        }
    )


async def update_page(page):
    table.update_item(
        Key={'id': page.id},
        UpdateExpression="SET name = :n, description = :d",
        ExpressionAttributeValues={":n": page.name, ":d": page.description},
    )


async def delete_page(page_id):
    table.delete_item(Key={'id': page_id})


async def update_posts_counter(page_id: int, field):
    match field:
        case "post_created":
            await update_page_statistics(page_id, 'amount_of_posts')
        case "post_deleted":
            await update_page_statistics(page_id, 'amount_of_posts', False)


async def update_likes_counter(page_id: int, field):
    match field:
        case "like_created":
            await update_page_statistics(page_id, 'amount_of_likes')
        case "like_deleted":
            await update_page_statistics(page_id, 'amount_of_likes', False)


async def update_followers_counter(page_id: int, field):
    match field:
        case "follower_added":
            await update_page_statistics(page_id, 'amount_of_followers')
        case "follower_deleted":
            await update_page_statistics(page_id, 'amount_of_followers', False)


async def update_page_statistics(page_id: int, value, increase=True):
    table.update_item(
        Key={'id': page_id},
        UpdateExpression=f"ADD counters.{value} :value",
        ExpressionAttributeValues={":value": 1 if increase else -1},
    )


async def retrieve_pages_statistics(user_id, page_id=None):
    if not page_id:
        return table.query(KeyConditionExpression="user_id=:user", ExpressionAttributeValues={":user": user_id})
    response = table.get_item(Key={'page_id': page_id, 'user_id': user_id})
    if not ('Item' in response):
        return 404
    return response
