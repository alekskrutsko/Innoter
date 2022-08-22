from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet

from apps.user.models import User
from apps.user.utils import UserMixin


class UserViewSet(UserMixin):
    queryset = User.objects.all()
