from rest_framework.permissions import BasePermission
from apps.user.models import User


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Roles.ADMIN

