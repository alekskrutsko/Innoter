from rest_framework.permissions import BasePermission

from apps.page.models import Page


class IsOwner(BasePermission):
    def has_permission(self, request, view, **kwargs):
        if not view.kwargs.get("pk") or not Page.objects.filter(pk=view.kwargs["pk"]).exists():
            return False

        return request.user.pk == Page.objects.get(pk=view.kwargs["pk"]).owner.pk


class IsPublicPage(BasePermission):
    def has_permission(self, request, view, **kwargs):
        if not view.kwargs.get("pk") or not Page.objects.filter(pk=view.kwargs["pk"]).exists():
            return False

        page = Page.objects.get(pk=view.kwargs["pk"])
        return not page.is_private or page.followers.contains(request.user)
