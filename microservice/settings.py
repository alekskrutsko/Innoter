from pydantic import BaseSettings


class Settings(BaseSettings):
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBIT_QUEUE_NAME: str

    class Config:
        env_file = ".env"


settings = Settings()
