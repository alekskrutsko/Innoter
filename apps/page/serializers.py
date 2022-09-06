from rest_framework import serializers

from apps.page.models import Page
from apps.tag.models import Tag
from apps.user.models import User


class UserPageSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    followers = serializers.SlugRelatedField(many=True, read_only=True, slug_field="username")
    follow_requests = serializers.SlugRelatedField(many=True, read_only=True, slug_field="username")
    tags = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Tag.objects.all())
    is_private = serializers.BooleanField(required=True)

    # image_url = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = (
            "id",
            "uuid",
            "name",
            "description",
            "tags",
            "owner",
            "followers",
            "image",
            "is_private",
            "follow_requests",
        )

        extra_kwargs = {
            "owner": {"read_only": True},
            "followers": {"read_only": True},
            "follow_requests": {"read_only": True},
        }

    # def get_image_url(self, obj):
    #     try:
    #         url = S3Client.create_presigned_url(object_name=obj.image)
    #     except ParamValidationError:
    #         url = ''
    #     return url


class AdminOrModerPageSerializer(serializers.ModelSerializer):
    """Serializer for separate page for admins only"""

    owner = serializers.ReadOnlyField(source="owner.username")
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name", allow_null=True)
    followers = serializers.SlugRelatedField(many=True, read_only=True, slug_field="username", allow_null=True)
    unblock_date = serializers.DateTimeField(default=None)

    class Meta:
        model = Page
        fields = (
            "id",
            "name",
            "uuid",
            "description",
            "tags",
            "owner",
            "image",
            "followers",
            "is_private",
            "unblock_date",
            "is_permanently_blocked",
        )
        read_only_fields = (
            "id",
            "name",
            "uuid",
            "description",
            "tags",
            "owner",
            "image",
            "followers",
            "is_private",
        )


class PageListSerializer(serializers.ModelSerializer):
    is_permanently_blocked = serializers.BooleanField(default=False)

    class Meta:
        model = Page
        fields = (
            "id",
            "name",
            "uuid",
            "owner",
            "is_private",
            "unblock_date",
            "is_permanently_blocked",
        )


class FollowersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "title",
            "email",
        )


class FollowerSerializer(serializers.ModelSerializer):
    """Serializer for accepting follow request"""

    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email",)
