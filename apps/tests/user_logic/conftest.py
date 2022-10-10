import pytest
from model_bakery import baker

from apps.user.models import User


@pytest.fixture()
def user():
    return baker.make(User, role="admin")


@pytest.fixture()
def new_user():
    return baker.prepare(User)


@pytest.fixture()
def update_json(new_user: User):
    return {
        "email": new_user.email,
        "username": new_user.username,
        "password": new_user.password,
        "title": new_user.title,
        "image_s3_path": new_user.image_s3_path,
    }


@pytest.fixture()
def expected_json(user: User):
    return {
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "image_s3_path": user.image_s3_path,
        "title": user.title,
        "refresh_token": user.refresh_token,
        "is_blocked": user.is_blocked,
    }


@pytest.fixture()
def expected_update_json(user: User, new_user: User):
    return {
        "email": new_user.email,
        "username": new_user.username,
        "role": user.role,
        "title": new_user.title,
        "image_s3_path": new_user.image_s3_path,
        "refresh_token": new_user.refresh_token,
        "is_blocked": new_user.is_blocked,
    }
