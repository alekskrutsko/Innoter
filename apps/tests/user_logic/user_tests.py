from io import BytesIO

import pytest
from PIL import Image
from rest_framework import status
from rest_framework.test import force_authenticate

from apps.user.models import User
from apps.user.views import UserViewSet

register_view = UserViewSet.as_view({"post": "register"})
login_view = UserViewSet.as_view({"post": "login"})
users_view = UserViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"})
list_view = UserViewSet.as_view({"get": "list"})
block_view = UserViewSet.as_view({"put": "block"})
unblock_view = UserViewSet.as_view({"put": "unblock"})
avatar_view = UserViewSet.as_view({"post": "set_avatar"})

pytestmark = pytest.mark.django_db


class TestUserEndpoints:
    endpoint = "/authentication/users/"

    def test_register(
        self,
        new_user,
        api_factory,
    ):
        user_json = {
            "user": {
                "email": new_user.email,
                "username": new_user.username,
                "password": new_user.password,
                "role": new_user.role,
                "title": new_user.title,
            }
        }

        request = api_factory.post(
            f"{self.endpoint}register",
            user_json,
            format="json",
        )

        response = register_view(request)

        assert response.status_code == status.HTTP_201_CREATED

    def test_login(self, user, api_factory):
        login_json = {
            "user": {
                "email": "test@gmail.com",
                "password": "qweasdzxc",
            }
        }

        request = api_factory.post(
            f"{self.endpoint}login",
            login_json,
            format="json",
        )

        response = login_view(request)
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('access_token') is not None

    def test_list(self, user, api_factory):
        request = api_factory.get(self.endpoint)

        force_authenticate(request, user=user, token=user.access_token)
        response = list_view(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == User.objects.count()

    def test_retrieve(
        self,
        user,
        expected_json,
        api_factory,
    ):
        request = api_factory.get(f"{self.endpoint}{user.pk}/")
        force_authenticate(request, user=user, token=user.access_token)
        request.COOKIES["access_token"] = user.access_token
        request.COOKIES["refresh_token"] = user.refresh_token

        response = users_view(request, pk=user.pk)
        expected_json["access_token"] = user.access_token

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_json
        assert response.cookies["access_token"].value == user.access_token

    def test_update(
        self,
        user,
        new_user,
        update_json,
        expected_update_json,
        api_factory,
    ):
        old_user = User.objects.get(pk=user.pk)

        request = api_factory.put(
            f"{self.endpoint}{old_user.pk}/",
            update_json,
            format="json",
        )

        force_authenticate(request, user=new_user, token=new_user.access_token)
        response = users_view(request, pk=old_user.pk)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_update_json

    def test_delete(self, user, api_factory):
        user_quantity = User.objects.all().count()
        request = api_factory.delete(f"{self.endpoint}/{user.pk}/")

        force_authenticate(request, user=user, token=user.access_token)
        response = users_view(request, pk=user.pk)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert User.objects.all().count() == user_quantity - 1

    def test_block(self, user, new_user, api_factory):
        user_to_block = new_user
        user_to_block.save()

        request = api_factory.put(f"{self.endpoint}/{user_to_block.pk}/block/")
        force_authenticate(request, user=user, token=user.access_token)
        response = block_view(request, pk=user_to_block.pk)

        assert response.status_code == status.HTTP_200_OK
        assert User.objects.get(pk=user_to_block.pk).is_blocked is True

    def test_unblock(self, user, new_user, api_factory):
        user_to_unblock = new_user
        user_to_unblock.is_blocked = True
        user_to_unblock.save()

        request = api_factory.put(f"{self.endpoint}/{user_to_unblock.pk}/unblock/")
        force_authenticate(request, user=user, token=user.access_token)
        response = unblock_view(request, pk=user_to_unblock.pk)

        assert response.status_code == status.HTTP_200_OK
        assert User.objects.get(pk=user_to_unblock.pk).is_blocked is False

    def test_upload_avatar_image(self, user, api_factory):
        file = BytesIO()
        image = Image.new('RGB', size=(10, 10), color=(155, 100, 0))
        image.save(file, 'jpeg')
        file.name = 'test.jpeg'
        file.seek(0)
        request = api_factory.post(
            f"{self.endpoint}set_avatar",
            {
                "image": file,
            },
        )
        force_authenticate(request, user=user, token=user.access_token)
        response = avatar_view(request)
        assert response.status_code == status.HTTP_200_OK
