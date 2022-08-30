from datetime import datetime, timedelta

import jwt
from django.db import models
from django.contrib.auth.models import AbstractUser

from Innotter import settings


class User(AbstractUser):
    class Roles(models.TextChoices):
        USER = "user"
        MODERATOR = "moderator"
        ADMIN = "admin"

    email = models.EmailField(unique=True)
    username = models.CharField(db_index=True, max_length=255, unique=True)
    image_s3_path = models.CharField(max_length=200, null=True, blank=True)
    role = models.CharField(max_length=9, choices=Roles.choices)
    title = models.CharField(max_length=80)
    is_blocked = models.BooleanField(default=False)
    refresh_token = models.CharField(max_length=255, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    @property
    def access_token(self):
        return self._generate_access_jwt_token()

    @property
    def set_and_get_refresh_token(self):
        refresh_token = self._generate_refresh_token()
        self.refresh_token = refresh_token
        self.save()
        return refresh_token

    def update_refresh_token(self):
        self.refresh_token = self._generate_refresh_token()
        self.save()

    def _generate_access_jwt_token(self):
        dt = datetime.now() + timedelta(minutes=5)
        token = jwt.encode(
            {"id": self.pk, "exp": int(dt.strftime("%s"))},
            settings.SECRET_KEY,
            # algorithm="HS256",   //default one
        )

        return token

    def _generate_refresh_token(self):
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode(
            {"exp": int(dt.strftime("%s"))},
            settings.SECRET_KEY,
            # algorithm="HS256",
        )

        return token
