import pytest
from rest_framework import status
from rest_framework.test import force_authenticate

from apps.tag.views import TagViewSet
from apps.tests.user_logic.conftest import user

pytestmark = pytest.mark.django_db

tag_view = TagViewSet.as_view({"get": "retrieve", "post": "create", "put": "update", "delete": "destroy"})
list_view = TagViewSet.as_view({"get": "list"})


class TestTagEndpoint:
    endpoint = "tag/tags/"

    def test_create(self, user: user, new_tag, api_factory):
        request = api_factory.post(f"{self.endpoint}", {"name": new_tag.name}, format="json")

        force_authenticate(request, user=user, token=user.access_token)

        response = tag_view(request)

        assert response.status_code == status.HTTP_201_CREATED

    def test_retrieve(self, user: user, tag, api_factory):
        request = api_factory.get(f"{self.endpoint}/{tag.pk}/")
        force_authenticate(request, user=user, token=user.access_token)

        response = tag_view(request, pk=tag.pk)

        assert response.status_code == status.HTTP_200_OK

    def test_update(self, user: user, tag, new_tag, api_factory):
        request = api_factory.put(f"{self.endpoint}/{tag.pk}/", {"name": new_tag.name}, format="json")
        force_authenticate(request, user=user, token=user.access_token)

        response = tag_view(request, pk=tag.pk)

        assert response.status_code == status.HTTP_200_OK

    def test_destroy(self, user: user, tag, api_factory):
        request = api_factory.delete(f"{self.endpoint}{tag.pk}")
        force_authenticate(request, user=user, token=user.access_token)

        response = tag_view(request, pk=tag.pk)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_list(self, user: user, api_factory):
        request = api_factory.get(f"{self.endpoint}/")
        force_authenticate(request, user=user, token=user.access_token)

        response = list_view(request)

        assert response.status_code == status.HTTP_200_OK
