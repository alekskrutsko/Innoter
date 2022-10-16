import pytest
from model_bakery import baker

from apps.page.models import Page


@pytest.fixture()
def page():
    return baker.make(Page)


@pytest.fixture()
def new_page():
    return baker.prepare(Page)


@pytest.fixture()
def expected_json(page: Page):
    return {
        "id": page.pk,
        "uuid": page.uuid,
        "name": page.name,
        "description": page.description,
        "owner": page.owner.username,
        "is_private": page.is_private,
        "unblock_date": page.unblock_date,
        "is_permanently_blocked": page.is_permanently_blocked,
    }


@pytest.fixture()
def update_json(new_page: Page):
    return {
        "uuid": new_page.uuid,
        "name": new_page.name,
        "description": new_page.description,
    }


@pytest.fixture()
def expected_update_json(page: Page, new_page: Page):
    return {
        "id": page.pk,
        "uuid": new_page.uuid,
        "name": new_page.name,
        "description": new_page.description,
        "owner": page.owner.username,
        "is_private": page.is_private,
        "unblock_date": page.unblock_date,
        "is_permanently_blocked": page.is_permanently_blocked,
    }


@pytest.fixture()
def temp_block_json():
    return {"page": {"block_time": "minutes 5"}}


@pytest.fixture()
def perm_block_json():
    return {"page": {"permanent_block": "true"}}
