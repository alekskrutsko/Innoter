from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("apps.user.urls", namespace="authentication")),
    path("api/", include("apps.page.urls", namespace="page")),
    path("api/", include("apps.tag.urls", namespace="tag")),
    path("api/", include("apps.post.urls", namespace="post")),
]
