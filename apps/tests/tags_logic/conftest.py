import pytest
from model_bakery import baker

from apps.tag.models import Tag


@pytest.fixture()
def tag():
    return baker.make(Tag)


@pytest.fixture()
def new_tag():
    return baker.prepare(Tag)
