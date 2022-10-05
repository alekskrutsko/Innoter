from datetime import datetime

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import DestroyModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.page.permissions import IsAdminOrModerator
from apps.user.models import User
from apps.user.permissions import IsAdmin, IsOwner
from apps.user.serializers import (
    UserLoginSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserUploadAvatarSerializer,
)
from apps.user.services import upload_photo_to_s3
from innotter.basic_mixin import GetPermissionsMixin, GetSerializerMixin


class UserMixin(
    GetSerializerMixin,
    GetPermissionsMixin,
    GenericViewSet,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
):
    serializer_classes = {
        "update": UserSerializer,
        "partial_update": UserSerializer,
        "retrieve": UserSerializer,
        "list": UserSerializer,
        "register": UserRegistrationSerializer,
        "login": UserLoginSerializer,
        "block": UserSerializer,
        "unblock": UserSerializer,
        "set_avatar": UserUploadAvatarSerializer,
    }

    permission_classes = {
        "update": (
            IsAuthenticated,
            (IsAdmin | IsOwner),
        ),
        "partial_update": (
            IsAuthenticated,
            (IsAdmin | IsOwner),
        ),
        "retrieve": (
            IsAuthenticated,
            (IsAdmin | IsOwner),
        ),
        "list": (
            IsAuthenticated,
            IsAdmin,
        ),
        "destroy": (
            IsAuthenticated,
            (IsAdmin | IsOwner),
        ),
        "register": (AllowAny,),
        "login": (AllowAny,),
        "block": (
            IsAuthenticated,
            IsAdminOrModerator,
        ),
        "unblock": (
            IsAuthenticated,
            IsAdminOrModerator,
        ),
        "set_avatar": (
            IsAuthenticated,
            IsOwner,
        ),
    }

    def retrieve(self, request, *args, **kwargs):
        if not User.objects.filter(pk=kwargs["pk"]).exists():
            return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(User.objects.get(pk=kwargs["pk"]))

        access_token = request.COOKIES["access_token"]
        response_dict = {"access_token": access_token}
        response_dict.update(serializer.data)
        response = Response(response_dict, status=status.HTTP_200_OK)
        response.set_cookie("access_token", access_token)

        return response

    @action(
        detail=False,
        methods=("post",),
    )
    def login(self, request):
        user = request.data.get(
            "user",
        )
        user_model = User.objects.get(email=user["email"])

        if user_model.is_blocked:
            return Response(
                {"detail": "You are blocked."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_model.last_login = datetime.now()
        user_model.save()

        serializer = self.get_serializer(data=user)
        serializer.is_valid(raise_exception=True)

        response = Response(serializer.data, status=status.HTTP_200_OK)

        response.set_cookie(
            "access_token",
            serializer.data.get(
                "access_token",
            ),
            httponly=True,
        )
        response.set_cookie(
            "refresh_token",
            serializer.data.get(
                "refresh_token",
            ),
            httponly=True,
        )

        return response

    @action(detail=False, methods=("post",))
    def register(self, request):
        user = request.data.get(
            "user",
        )

        serializer = self.get_serializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=("put",),
    )
    def block(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs.get("pk", None))

        user.is_blocked = True
        user.save()

        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=("put",),
    )
    def unblock(self, request, *args, **kwargs):
        user = User.objects.get(pk=kwargs.get("pk", None))

        user.is_blocked = False
        user.save()

        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=("put",),
    )
    def set_avatar(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        image_s3_path = upload_photo_to_s3(request)

        return Response(image_s3_path, status=status.HTTP_200_OK)
