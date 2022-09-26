from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from apps.page.permissions import IsAdminOrModerator
from apps.tag.models import Tag
from apps.tag.permissions import IsOwner, IsPublicPage
from apps.tag.serializers import TagSerializer
from innotter.basic_mixin import GetPermissionsMixin


class TagViewSet(
    GetPermissionsMixin,
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
