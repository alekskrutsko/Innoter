from rest_framework.permissions import BasePermission

from apps.page.models import Page


class IsOwner(BasePermission):
    def has_permission(self, request, view, **kwargs):
        return request.user.pk == Page.objects.get(pk=view.kwargs["page_pk"]).owner.pk


class IsPublicPage(BasePermission):
    def has_permission(self, request, view, **kwargs):
        if request.method == "GET":
            page = Page.objects.get(pk=view.kwargs["page_pk"])
            return not page.is_private or page.followers.contains(request.user)
        else:
            return False


class IsBlockedPage(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.is_permanently_blocked:
            return False
        elif obj.is_temporary_blocked():
            return False
        else:
            return True
