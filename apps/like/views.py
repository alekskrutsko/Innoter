from django.shortcuts import render
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, \
    ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from Innotter.basic_mixin import GetSerializerMixin, GetPermissionsMixin
from apps.like.models import Like
from apps.like.permissions import IsBlockedPage, IsPublicPage, IsOwner
from apps.like.serializers import CreateLikeSerializer, LikeSerializer
from apps.like.services import create_like, delete_like
from apps.page.permissions import IsAdminOrModerator
from apps.post.models import Post
from apps.user.models import User


class LikeViewSet(GetSerializerMixin,
                  GetPermissionsMixin,
                  CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  ListModelMixin,
                  GenericViewSet):
    queryset = Like.objects.all()

    permission_classes = {
        "create": (
            IsAuthenticated,
            (IsPublicPage | IsAdminOrModerator),
            IsBlockedPage,
        ),
        "retrieve": (
            IsAuthenticated,
            (IsPublicPage | IsOwner | IsAdminOrModerator),
            IsBlockedPage,
        ),
        "list": (
            IsAuthenticated,
            IsAdminOrModerator,
        ),
        "destroy": (
            IsAuthenticated,
            (IsOwner | IsAdminOrModerator),
            IsBlockedPage,
        ),
    }
    serializer_classes = {
        "create": CreateLikeSerializer,
        "retrieve": LikeSerializer,
        "list": LikeSerializer,
    }

    def perform_create(self, serializer):

        if not Like.objects.filter(
                owner=self.request.user,
                post__id=serializer.validated_data.get("post").pk,
        ).exists():
            create_like(
                current_user=self.request.user,
                liked_post=serializer.validated_data.get("post"),
            )
        else:
            delete_like(
                current_user=self.request.user,
                liked_post=serializer.validated_data.get("post"),
            )

    def get_queryset(self):
        if self.request.data.get("post"):
            return Like.objects.filter(
                post=Post.objects.get(pk=self.request.data.get("post"))
            )
        elif (
                self.request.user.role == User.Roles.ADMIN
                and not self.request.data.get("post")
        ):
            return Like.objects.all()
