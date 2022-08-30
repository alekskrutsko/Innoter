from django.urls import path, include
from rest_framework.routers import SimpleRouter

from apps.post.views import PostViewSet, AllPostViewSet


router = SimpleRouter()
router.register(r"posts", PostViewSet, basename="page")

app_name = "posts"

urlpatterns = [
    path("", include(router.urls)),
    path("posts/", AllPostViewSet.as_view({"get": "get_all_posts"})),
]

