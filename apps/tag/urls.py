from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework.urlpatterns import format_suffix_patterns

from apps.tag.views import TagViewSet

router = SimpleRouter()
router.register("tags", TagViewSet, basename="tags")

app_name = "Tags"

urlpatterns = [
    path("", include(router.urls)),
]
