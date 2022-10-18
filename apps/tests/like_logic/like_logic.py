import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import force_authenticate

from apps.like.models import Like
from apps.like.views import LikeViewSet
from apps.tests.like_logic.conftest import post
from apps.tests.user_logic.conftest import user

like_viewset = LikeViewSet.as_view({"get": "retrieve", "post": "create", "delete": "destroy"})
list_viewset = LikeViewSet.as_view({"get": "list"})
pytestmark = pytest.mark.django_db


class TestLikeEndpoint:
    endpoint = "/likes/likes/"

    def test_create(self, user: user, post: post, api_factory):
        request = api_factory.post(self.endpoint, {"post": post.pk}, format="json")
        force_authenticate(request, user=user, token=user.access_token)

        response = like_viewset(request)

        assert response.status_code == status.HTTP_201_CREATED

    def test_delete_if_exists(self, user: user, post: post, api_factory):
        baker.make(Like, owner=user, post=post)

        request = api_factory.post(self.endpoint, {"post": post.pk}, format="json")
        force_authenticate(request, user=user, token=user.access_token)

        response = like_viewset(request)

        assert response.status_code == status.HTTP_201_CREATED

    def test_retrieve(self, user: user, post: post, api_factory):
        like = baker.make(Like, owner=user, post=post)

        request = api_factory.get(f"{self.endpoint}/{like.pk}", {"post": post.pk}, format="json")
        force_authenticate(request, user=user, token=user.access_token)

        response = like_viewset(request, pk=like.pk)

        assert response.status_code == status.HTTP_200_OK

    def test_destroy(self, user: user, post: post, api_factory):
        like = baker.make(Like, owner=user, post=post)

        request = api_factory.delete(f"{self.endpoint}/{like.pk}", {"post": post.pk}, format="json")
        force_authenticate(request, user=user, token=user.access_token)

        response = like_viewset(request, pk=like.pk)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_list(self, user: user, api_factory):
        request = api_factory.get(f"{self.endpoint}", format="json")
        force_authenticate(request, user=user, token=user.access_token)

        response = list_viewset(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == Like.objects.all().count()
