import pytest
from model_bakery import baker

from apps.page.models import Page
from apps.post.models import Post


@pytest.fixture()
def post(page: Page):
    return baker.make(Post, page=page)


@pytest.fixture()
def new_post():
    return baker.prepare(Post)


@pytest.fixture()
def update_json(new_post: Post):
    return {
        "content": new_post.content,
    }


@pytest.fixture()
def expected_update_json(new_post: Post):
    return {
        "content": new_post.content,
    }
