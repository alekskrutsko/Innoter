from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from apps.page.models import Page
from apps.page.permissions import IsAdminOrModerator
from apps.post.models import Post
from apps.post.permissions import IsBlockedPage, IsOwner, IsPublicPage
from apps.post.serializers import ListPostSerializer, PostSerializer, UpdatePostSerializer
from apps.post.services import send_email_to_followers
from apps.producer import publish
from innotter.basic_mixin import GetPermissionsMixin


class PostViewSet(GetPermissionsMixin, ModelViewSet):
    detail_serializer_classes = {
        "update": UpdatePostSerializer,
    }
    permission_classes = {
        "partial_update": (
            IsAuthenticated,
            (IsOwner | IsAdminOrModerator),
            IsBlockedPage,
        ),
        "update": (
            IsAuthenticated,
            IsBlockedPage,
            (IsOwner | IsAdminOrModerator),
        ),
        "destroy": (
            IsAuthenticated,
            IsBlockedPage,
            (IsOwner | IsAdminOrModerator),
        ),
        "create": (IsAuthenticated, IsOwner, IsBlockedPage),
        "list": (
            IsAuthenticated,
            (IsPublicPage | IsOwner | IsAdminOrModerator),
            IsBlockedPage,
        ),
        "retrieve": (
            IsAuthenticated,
            (IsPublicPage | IsOwner | IsAdminOrModerator),
            IsBlockedPage,
        ),
    }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        send_email_to_followers(serializer.data, self.kwargs.get('page_pk'))
        publish("post_created", self.kwargs.get('page_pk'))
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        publish("post_deleted", self.kwargs.get('page_pk'))
        return response

    def get_serializer_class(self):
        if self.action == "update":
            return self.detail_serializer_classes.get(self.action)
        return PostSerializer

    def get_queryset(self):
        return Post.objects.filter(page=Page.objects.get(pk=self.kwargs.get('page_pk')))


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
