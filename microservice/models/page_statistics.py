from pydantic import BaseModel


class Page(BaseModel):
    id: int
    owner: int
    name: str
    description: str = ""
    amount_of_posts: int = 0
    amount_of_likes: int = 0
    amount_of_followers: int = 0


def response_model(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def error_response_model(error, code, message):
    return {"error": error, "code": code, "message": message}
