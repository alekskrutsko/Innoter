from pydantic import BaseSettings


class Settings(BaseSettings):
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBIT_QUEUE_NAME: str
    AWS_DEFAULT_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DYNAMODB_TABLE_NAME: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
