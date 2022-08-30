from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.page.models import Page
from apps.page.permissions import IsAdminOrModerator
from apps.tag.models import Tag
from apps.tag.permissions import IsOwner, IsPublicPage
from apps.tag.serializers import TagSerializer


class TagViewSet(
    GenericViewSet,
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = {
        "create": (
            IsAuthenticated,
            (IsOwner | IsAdminOrModerator),
        ),
        "retrieve": (IsAuthenticated, (IsPublicPage | IsOwner | IsAdminOrModerator)),
        "destroy": (
            IsAuthenticated,
            (IsOwner | IsAdminOrModerator),
        ),
        "list": (
            IsAuthenticated,
            (IsPublicPage | IsOwner | IsAdminOrModerator),
        ),
    }
