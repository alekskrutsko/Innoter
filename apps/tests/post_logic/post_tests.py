import pytest
from rest_framework import status
from rest_framework.test import force_authenticate

from apps.page.models import Page
from apps.post.models import Post
from apps.post.views import AllPostViewSet, PostViewSet
from apps.tests.page_logic.conftest import page
from apps.tests.user_logic.conftest import user

pytestmark = pytest.mark.django_db
post_view = PostViewSet.as_view({"get": "retrieve", "post": "create", "put": "update", "delete": "destroy"})
list_view = PostViewSet.as_view({"get": "list"})
get_all_view = AllPostViewSet.as_view({"get": "list"})


class TestPostEndpoint:
    endpoint = "post/pages/"

    def test_create(self, user: user, page: page, new_post, api_factory, mocker):
        post_json = {
            "content": new_post.content,
        }

        request = api_factory.post(f"{self.endpoint}/{page.pk}/posts/", post_json, format="json")
        force_authenticate(request, user=user, token=user.access_token)

        mocker.patch("apps.post.permissions.IsOwner.has_permission", return_value=True)
        response = post_view(request, page_pk=page.pk)
        print(response.data)

        assert response.status_code == status.HTTP_201_CREATED

    def test_retrieve(
        self,
        user: user,
        page: page,
        post,
        api_factory,
    ):
        request = api_factory.get(f"{self.endpoint}/{page.pk}/posts/{post.pk}/")
        force_authenticate(request, user=user, token=user.access_token)

        response = post_view(request, page_pk=page.pk, pk=post.pk)

        assert response.status_code == status.HTTP_200_OK

    def test_update(
        self,
        user: user,
        page: page,
        post,
        update_json,
        expected_update_json,
        api_factory,
    ):
        request = api_factory.put(
            f"{self.endpoint}/{page.pk}/posts/{post.pk}/",
            update_json,
            format="json",
        )
        force_authenticate(request, user=user, token=user.access_token)

        response = post_view(request, page_pk=page.pk, pk=post.pk)

        assert response.status_code == 200
        assert response.data == expected_update_json

    def test_destroy(
        self,
        user: user,
        page: page,
        post,
        api_factory,
    ):
        posts = Post.objects.all().count()
        request = api_factory.delete(f"{self.endpoint}/{page.pk}/posts/{post.pk}/")
        force_authenticate(request, user=user, token=user.access_token)

        response = post_view(request, page_pk=page.pk, pk=post.pk)

        assert response.status_code == 204
        assert posts - 1 == Post.objects.all().count()

    def test_list(self, user: user, page: page, api_factory):
        request = api_factory.get(f"{self.endpoint}/{page.pk}/posts/")
        force_authenticate(request, user=user, token=user.access_token)

        response = list_view(request, page_pk=page.pk)

        assert response.status_code == 200
        assert len(response.data) == Post.objects.filter(page=Page.objects.get(pk=page.pk)).count()

    def test_get_all_posts(self, user: user, page: page, api_factory):
        request = api_factory.get("/post/posts/")
        force_authenticate(request, user=user, token=user.access_token)

        response = get_all_view(request)

        assert response.status_code == 200
        assert len(response.data) == Post.objects.all().count()
