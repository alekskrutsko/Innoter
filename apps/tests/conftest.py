import django
import pytest
from rest_framework.test import APIRequestFactory

django.setup()


@pytest.fixture()
def api_factory():
    return APIRequestFactory()
