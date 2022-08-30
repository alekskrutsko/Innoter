from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework.urlpatterns import format_suffix_patterns

from apps.page.views import PagesListViewSet, CurrentUserPagesViewSet

router = SimpleRouter()
router.register(r"pages", PagesListViewSet, basename="pages")
router.register(r"my-pages", CurrentUserPagesViewSet, basename="my-pages")

app_name = "Pages"
urlpatterns = [
    path("", include(router.urls)),
]

urlpatterns = format_suffix_patterns(urlpatterns)
