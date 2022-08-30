from rest_framework.permissions import BasePermission
from apps.user.models import User


class IsAdminOrModerator(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.role == User.Roles.ADMIN
            or request.user.role == User.Roles.MODERATOR
        )


class IsPageOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsPrivatePage(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.is_private


class IsBlockedPage(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.is_permanently_blocked or obj.is_temporary_blocked():
            return False
        return True
