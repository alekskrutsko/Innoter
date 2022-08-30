from rest_framework.permissions import BasePermission

from apps.like.models import Like
from apps.post.models import Post


class IsPublicPage(BasePermission):
    def has_permission(self, request, view, **kwargs):
        if request.method != "POST":
            page = Like.objects.get(pk=view.kwargs["pk"]).post.page
            return not page.is_private or page.followers.contains(request.user)
        post = Post.objects.get(pk=request.data.get("post")).page
        return not post.is_private or post.followers.contains(request.user)


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsBlockedPage(BasePermission):
    def has_permission(self, request, view):
        if request.method != "POST":
            page = Like.objects.get(pk=view.kwargs["pk"]).post.page
            return not page.is_permanently_blocked and page.is_temporary_blocked()
        page = Post.objects.get(pk=request.data.get("post")).page
        return not page.is_permanently_blocked and page.is_temporary_blocked()
