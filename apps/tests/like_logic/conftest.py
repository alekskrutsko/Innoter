import pytest
from model_bakery import baker

from apps.post.models import Post
from apps.tests.page_logic.conftest import page


@pytest.fixture()
def post(page: page):
    return baker.make(Post, page=page)
