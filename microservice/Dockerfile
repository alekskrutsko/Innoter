FROM python:3.10.4

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install poetry
WORKDIR /app
RUN poetry add fastapi pydantic uvicorn pika aio-pika

COPY . /app/
