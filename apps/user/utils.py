from datetime import datetime

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import (
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from Innotter.basic_mixin import GetPermissionsMixin, GetSerializerMixin
from apps.user.models import User
from apps.user.permissions import IsAdmin
from apps.user.serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
)


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
        "update_me": UserSerializer,
        "me": UserSerializer,
        "block": UserSerializer,
        "unblock": UserSerializer,
    }

    permission_classes = {
        "update": (
            IsAuthenticated,
            IsAdmin,
        ),
        "partial_update": (
            IsAuthenticated,
            IsAdmin,
        ),
        "retrieve": (
            IsAuthenticated,
            IsAdmin,
        ),
        "list": (
            IsAuthenticated,
            IsAdmin,
        ),
        "destroy": (
            IsAuthenticated,
            IsAdmin,
        ),
        "register": (AllowAny,),
        "login": (AllowAny,),
    }

    def retrieve(self, request, *args, **kwargs):
        if User.objects.filter(pk=kwargs["pk"]).exists():
            return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(User.objects.get(pk=kwargs["pk"]))

        access_token = request.COOKIES["access_token"]
        response_dict = {"access_token": access_token}
        response_dict.update(serializer.data)
        response = Response(response_dict, status=status.HTTP_200_OK)
        response.set_cookie("access_token", access_token)

        return response

    def update(self, request, *args, **kwargs):
        if not User.objects.filter(pk=kwargs["pk"]).exists():
            return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

        serializer_data = request.data.get(
            "user",
        )

        serializer = self.get_serializer(
            User.objects.get(pk=kwargs.get("pk")),
            data=serializer_data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

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
