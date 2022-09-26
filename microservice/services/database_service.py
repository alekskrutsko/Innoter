import boto3

from microservice.settings import settings

dynamodb = boto3.resource(
    "dynamodb",
    region_name=settings.AWS_DEFAULT_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)
table = dynamodb.Table(settings.AWS_DYNAMODB_TABLE_NAME)


async def create_table():
    dynamodb.create_table(
        TableName=settings.AWS_DYNAMODB_TABLE_NAME,
        KeySchema=[{'AttributeName': 'page_id', 'KeyType': 'HASH'}, {"AttributeName": "user_id", "KeyType": "RANGE"}],
        AttributeDefinitions=[
            {'AttributeName': 'page_id', 'AttributeType': 'S'},
            {"AttributeName": "user_id", "AttributeType": "S"},
        ],
        ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10},
    )
