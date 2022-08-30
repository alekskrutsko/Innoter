from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from Innotter.basic_mixin import GetPermissionsMixin
from apps.page.permissions import IsAdminOrModerator
from apps.post.permissions import IsOwner, IsBlockedPage, IsPublicPage
from apps.post.models import Post
from apps.post.serializers import (
    PostSerializer,
    ListPostSerializer,
    UpdatePostSerializer,
)


class PostViewSet(ModelViewSet):
    detail_serializer_classes = {
        "update": UpdatePostSerializer,
    }
    queryset = Post.objects.all()
    permission_classes = {
        "partial_update": (
            IsAuthenticated,
            IsOwner,
            ~IsBlockedPage,
        ),
        "update": (
            IsAuthenticated,
            ~IsBlockedPage,
        ),
        "destroy": (
            IsAuthenticated,
            ~IsBlockedPage,
            (IsOwner | IsAdminOrModerator),
        ),
        "create": (IsAuthenticated, IsOwner, ~IsBlockedPage),
        "list": (
            IsAuthenticated,
            (IsPublicPage | IsOwner | IsAdminOrModerator),
            ~IsBlockedPage,
        ),
        "retrieve": (
            IsAuthenticated,
            (IsPublicPage | IsOwner | IsAdminOrModerator),
            ~IsBlockedPage,
        ),
    }

    def get_serializer_class(self):
        if self.action == "update":
            return self.detail_serializer_classes.get(self.action)
        return PostSerializer


class AllPostViewSet(GenericViewSet, ListModelMixin):
    queryset = Post.objects.all()
    permission_classes = (
        IsAuthenticated,
        IsAdminOrModerator,
    )
    serializer_class = ListPostSerializer

    @action(
        detail=False,
        methods=("get",),
    )
    def get_all_posts(self, request):
        data = ListPostSerializer(data=Post.objects.all(), many=True)
        data.is_valid()
        return Response(data=data.data, status=status.HTTP_200_OK)
