from django.contrib.auth import authenticate
from rest_framework import serializers

from apps.user.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    role = serializers.CharField(default="user")
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "title",
            "role",
            "password",
            "access_token",
            "refresh_token",
        )

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.update_refresh_token()
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, write_only=True)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, required=True, write_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get(
            "email",
        )
        password = data.get(
            "password",
        )

        if not email:
            raise serializers.ValidationError("An email address is required to log in.")

        if not password:
            raise serializers.ValidationError("A password is required to log in.")

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("A user with this email and password was not found.")

        if not user.is_active:
            raise serializers.ValidationError("This user has been blocked.")

        return {
            "email": user.email,
            "username": user.username,
            "access_token": user.access_token,
            "refresh_token": user.set_and_get_refresh_token,
        }


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "title",
            "image_s3_path",
            "role",
            "refresh_token",
            "is_blocked",
        )
        extra_kwargs = {
            "refresh_token": {"read_only": True},
            "is_blocked": {"read_only": True},
            "role": {"read_only": True},
        }

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if password:
            instance.set_password(password)

        instance.save()

        return instance


class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username"]
        extra_kwargs = {
            "username": {"read_only": True},
        }


class UserUploadAvatarSerializer(serializers.Serializer):
    img = serializers.FileField()
