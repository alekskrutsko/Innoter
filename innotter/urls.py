from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("authentication/", include("apps.user.urls", namespace="authentication")),
    path("page/", include("apps.page.urls", namespace="page")),
    path("tag/", include("apps.tag.urls", namespace="tag")),
    path("post/", include("apps.post.urls", namespace="post")),
    path("likes/", include("apps.like.urls", namespace="likes")),
]
