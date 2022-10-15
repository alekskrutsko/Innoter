from rest_framework.permissions import BasePermission

from apps.user.models import User


class IsAdminOrModerator(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in (User.Roles.ADMIN, User.Roles.MODERATOR)


class IsPageOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsPrivatePage(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.is_private


class IsBlockedPage(BasePermission):
    def has_object_permission(self, request, view, obj):
        return not obj.is_permanently_blocked and obj.is_temporary_blocked()
