from datetime import datetime
from io import BytesIO

import pytest
from django.db.models import Q
from model_bakery import baker
from PIL import Image
from rest_framework import status
from rest_framework.test import force_authenticate

from apps.page.models import Page
from apps.page.serializers import PageListSerializer
from apps.page.views import CurrentUserPagesViewSet, PagesListViewSet
from apps.tag.models import Tag
from apps.tests.user_logic.conftest import new_user, user
from apps.user.models import User

pytestmark = pytest.mark.django_db

page_view = PagesListViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
    }
)
list_view = PagesListViewSet.as_view({"get": "list"})
my_page_view = CurrentUserPagesViewSet.as_view(
    {
        "post": "create",
        "get": "retrieve",
        "put": "update",
        "delete": "destroy",
    }
)

block_view = PagesListViewSet.as_view({"put": "block"})
unblock_view = PagesListViewSet.as_view({"put": "unblock"})

list_page_view = PagesListViewSet.as_view({"get": "list"})
get_blocked_view = PagesListViewSet.as_view({"get": "blocked"})
followers_view = PagesListViewSet.as_view({"get": "followers"})
follow_view = PagesListViewSet.as_view({"post": "follow"})
unfollow_view = PagesListViewSet.as_view({"post": "unfollow"})
follow_requests_view = CurrentUserPagesViewSet.as_view({"get": "page_follow_requests"})
accept_follow_request_view = CurrentUserPagesViewSet.as_view({"post": "accept_follow_request"})
deny_follow_request_view = CurrentUserPagesViewSet.as_view({"post": "deny_follow_request"})
accept_all_requests_view = CurrentUserPagesViewSet.as_view({"post": "accept_all_follow_requests"})
deny_all_requests_view = CurrentUserPagesViewSet.as_view({"post": "deny_all_follow_requests"})
get_tags_view = CurrentUserPagesViewSet.as_view({"get": "tags"})
add_tag_view = CurrentUserPagesViewSet.as_view({"post": "add_tag_to_page"})
remove_tag_view = CurrentUserPagesViewSet.as_view({"delete": "remove_tag_from_page"})
set_private_view = CurrentUserPagesViewSet.as_view({"put": "set_private"})
set_public_view = CurrentUserPagesViewSet.as_view({"put": "set_public"})
set_avatar_view = CurrentUserPagesViewSet.as_view({"put": "set_avatar"})


class TestPageEndpoint:
    endpoint = "page/"

    def test_create(self, user, new_page, api_factory):
        page_json = {
            "uuid": new_page.uuid,
            "name": new_page.name,
            "description": new_page.description,
            "is_private": new_page.is_private,
        }

        request = api_factory.post(f"{self.endpoint}/my-pages/", page_json, format="json")
        force_authenticate(request, user=user, token=user.access_token)

        response = my_page_view(request)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data == PageListSerializer(Page.objects.get(uuid=new_page.uuid)).data

    def test_retrieve(
        self,
        user,
        page,
        api_factory,
        expected_json,
    ):
        request = api_factory.get(f"{self.endpoint}/my-pages/{page.pk}/")
        force_authenticate(request, user=user, token=user.access_token)

        response = my_page_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_json

    def test_list(self, user, api_factory):
        request = api_factory.get(f"{self.endpoint}/my-pages/")
        force_authenticate(request, user=user, token=user.access_token)

        response = list_page_view(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == Page.objects.all().count()

    def test_update(self, user, page, update_json, expected_update_json, api_factory, mocker):
        request = api_factory.put(f"{self.endpoint}/my-pages/{page.pk}/", update_json, format="json")
        force_authenticate(request, user=user, token=user.access_token)
        mocker.patch("apps.page.permissions.IsPageOwner.has_object_permission", return_value=True)
        response = my_page_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_update_json

    def test_delete(self, user, page, api_factory):
        pages = Page.objects.all().count()
        request = api_factory.delete(f"{self.endpoint}/my-pages/{page.pk}/")
        force_authenticate(request, user=user, token=user.access_token)

        response = my_page_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert pages - 1 == Page.objects.all().count()

    def test_temp_block_page(
        self,
        user,
        page,
        temp_block_json,
        expected_json,
        api_factory,
    ):
        request = api_factory.put(f"{self.endpoint}/pages/{page.pk}/block/", temp_block_json, format="json")
        force_authenticate(request, user=user, token=user.access_token)

        response = block_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK
        assert not Page.objects.get(pk=page.pk).is_temporary_blocked()

    def test_temp_unblock_page(self, user, page, api_factory):
        request = api_factory.put(f"{self.endpoint}/pages/{page.pk}/unblock/", {"page": {}}, format="json")
        force_authenticate(request, user=user, token=user.access_token)

        response = unblock_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK
        assert Page.objects.get(pk=page.pk).is_temporary_blocked()

    def test_perm_block_page(
        self,
        user,
        page,
        perm_block_json,
        expected_json,
        api_factory,
    ):
        request = api_factory.put(f"{self.endpoint}/pages/{page.pk}/block/", perm_block_json, format="json")
        force_authenticate(request, user=user, token=user.access_token)

        response = block_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK
        assert Page.objects.get(pk=page.pk).is_permanently_blocked

    def test_perm_unblock_page(self, user, page, api_factory):
        request = api_factory.put(
            f"{self.endpoint}/pages/{page.pk}/unblock/", {"page": {"permanent_block": ""}}, format="json"
        )
        force_authenticate(request, user=user, token=user.access_token)

        response = unblock_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK
        assert not Page.objects.get(pk=page.pk).is_permanently_blocked

    def test_get_blocked_pages(
        self,
        user,
        api_factory,
    ):
        request = api_factory.get(f"{self.endpoint}/pages/blocked/")
        force_authenticate(request, user=user, token=user.access_token)

        response = get_blocked_view(request)

        assert response.status_code == status.HTTP_200_OK
        assert (
            len(response.data)
            == Page.objects.filter(
                Q(is_permanently_blocked=True) | (Q(unblock_date__isnull=False) & Q(unblock_date__gt=datetime.now()))
            ).count()
        )

    def test_get_followers(self, user: user, new_user: new_user, page, api_factory, mocker):
        new_user.save()
        page.followers.add(new_user)
        request = api_factory.get(f"{self.endpoint}/pages/{page.pk}/followers/")
        force_authenticate(request, user=user, token=user.access_token)

        mocker.patch("apps.page.permissions.IsPageOwner.has_object_permission", return_value=True)
        response = followers_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK

    def test_follow(
        self,
        user,
        page,
        api_factory,
    ):
        request = api_factory.post(f"{self.endpoint}/pages/{page.pk}/follow/")
        force_authenticate(request, user=user, token=user.access_token)

        response = follow_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK

    def test_unfollow(
        self,
        user,
        page,
        api_factory,
    ):
        request = api_factory.post(f"{self.endpoint}/pages/{page.pk}/unfollow/")
        force_authenticate(request, user=user, token=user.access_token)

        response = unfollow_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK

    def test_page_follow_requests(
        self,
        user,
        page,
        api_factory,
    ):
        request = api_factory.get(f"{self.endpoint}/my-pages/{page.pk}/follow-requests/")
        force_authenticate(request, user=user, token=user.access_token)

        response = follow_requests_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK

    def test_accept_follow_request(self, user, new_user, page, api_factory, mocker):
        new_user.save()
        page.follow_requests.add(new_user)
        request = api_factory.post(
            f"{self.endpoint}/my-pages/{page.pk}/accept-follower/", {"email": new_user.email}, format="json"
        )
        force_authenticate(request, user=user, token=user.access_token)

        mocker.patch("apps.page.permissions.IsPageOwner.has_object_permission", return_value=True)
        response = accept_follow_request_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK

    def test_deny_follow_request(self, user, new_user, page, api_factory, mocker):
        new_user.save()
        page.follow_requests.add(new_user)
        request = api_factory.post(
            f"{self.endpoint}/my-pages/{page.pk}/deny-follower/", {"email": new_user.email}, format="json"
        )
        force_authenticate(request, user=user, token=user.access_token)

        mocker.patch("apps.page.permissions.IsPageOwner.has_object_permission", return_value=True)
        response = deny_follow_request_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK

    def test_accept_all_follow_requests(self, user, page, api_factory, mocker):
        users = baker.make(User, _refresh_after_create=True, _quantity=4)
        page.follow_requests.add(*users)
        followers = page.followers.count()
        request = api_factory.post(f"{self.endpoint}/my-pages/{page.pk}/accept-all/")
        force_authenticate(request, user=user, token=user.access_token)

        mocker.patch("apps.page.permissions.IsPageOwner.has_object_permission", return_value=True)
        response = accept_all_requests_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK
        assert page.followers.count() == followers + 4

    def test_deny_all_follow_requests(self, user, page, api_factory, mocker):
        users = baker.make(User, _refresh_after_create=True, _quantity=4)
        page.follow_requests.add(*users)
        request = api_factory.post(f"{self.endpoint}/my-pages/{page.pk}/deny-all/")
        force_authenticate(request, user=user, token=user.access_token)

        mocker.patch("apps.page.permissions.IsPageOwner.has_object_permission", return_value=True)
        response = deny_all_requests_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK
        assert page.follow_requests.count() == 0

    def test_get_tags(self, user, page, api_factory, mocker):
        request = api_factory.get(f"{self.endpoint}/my-pages/{page.pk}/tags/")
        force_authenticate(request, user=user, token=user.access_token)

        mocker.patch("apps.page.permissions.IsPageOwner.has_object_permission", return_value=True)
        response = get_tags_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK

    def test_add_tag(self, user, page, api_factory, mocker):
        request = api_factory.post(f"{self.endpoint}/my-pages/{page.pk}/add-tag/", {"name": "first tag"}, format="json")
        force_authenticate(request, user=user, token=user.access_token)

        mocker.patch("apps.page.permissions.IsPageOwner.has_object_permission", return_value=True)
        response = add_tag_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK

    def test_remove_tag(self, user, page, api_factory, mocker):
        tag = baker.make(Tag)
        page.tags.add(tag)
        request = api_factory.delete(
            f"{self.endpoint}/my-pages/{page.pk}/remove-tag/", {"name": tag.name}, format="json"
        )
        force_authenticate(request, user=user, token=user.access_token)

        mocker.patch("apps.page.permissions.IsPageOwner.has_object_permission", return_value=True)
        response = remove_tag_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK

    def test_set_private(self, user, page, api_factory, mocker):
        page.owner = user
        page.save()
        request = api_factory.put(f"{self.endpoint}/my-pages/{page.pk}/set_private/")
        force_authenticate(request, user=user, token=user.access_token)

        response = set_private_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK

    def test_set_public(self, user, page, api_factory, mocker):
        page.owner = user
        page.save()
        request = api_factory.put(f"{self.endpoint}/my-pages/{page.pk}/set_public/")
        force_authenticate(request, user=user, token=user.access_token)

        mocker.patch("apps.page.permissions.IsPageOwner.has_object_permission", return_value=True)
        response = set_public_view(request, pk=page.pk)

        assert response.status_code == status.HTTP_200_OK

    def test_upload_avatar_image(self, user, page, api_factory):
        file = BytesIO()
        image = Image.new('RGB', size=(10, 10), color=(155, 100, 0))
        image.save(file, 'jpeg')
        file.name = 'test.jpeg'
        file.seek(0)
        request = api_factory.put(
            f"{self.endpoint}/my-pages/{page.pk}/set_avatar",
            {
                "image": file,
            },
        )
        force_authenticate(request, user=user, token=user.access_token)
        response = set_avatar_view(request, pk=page.pk)
        assert response.status_code == status.HTTP_200_OK
