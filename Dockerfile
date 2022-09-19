FROM python:3.10.4

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install poetry && poetry --version
WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false && poetry install

COPY . /app/
EXPOSE 8000
