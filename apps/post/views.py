from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from apps.page.permissions import IsAdminOrModerator
from apps.post.models import Post
from apps.post.permissions import IsBlockedPage, IsOwner, IsPublicPage
from apps.post.serializers import ListPostSerializer, PostSerializer, UpdatePostSerializer
from apps.post.services import send_email_to_followers


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        send_email_to_followers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
