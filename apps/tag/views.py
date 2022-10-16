from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.page.permissions import IsAdminOrModerator
from apps.tag.models import Tag
from apps.tag.permissions import ReadOnly
from apps.tag.serializers import TagSerializer
from innotter.basic_mixin import GetPermissionsMixin


class TagViewSet(GetPermissionsMixin, ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = {
        "create": (
            IsAuthenticated,
            IsAdminOrModerator,
        ),
        "update": (
            IsAuthenticated,
            IsAdminOrModerator,
        ),
        "retrieve": (IsAuthenticated, ReadOnly),
        "destroy": (
            IsAuthenticated,
            IsAdminOrModerator,
        ),
        "list": (
            IsAuthenticated,
            ReadOnly,
        ),
    }
