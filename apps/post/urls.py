from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

from apps.page.views import PagesListViewSet
from apps.post.views import AllPostViewSet, PostViewSet

router = SimpleRouter()
router.register("pages", PagesListViewSet)

post_router = routers.NestedSimpleRouter(router, r"pages", lookup="page")

post_router.register(r"posts", PostViewSet, basename="page")

app_name = "posts"

urlpatterns = [
    path("", include(post_router.urls)),
    path("posts/", AllPostViewSet.as_view({"get": "get_all_posts"})),
]
