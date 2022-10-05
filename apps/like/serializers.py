from rest_framework import serializers

from apps.like.models import Like


class CreateLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = (
            "id",
            "post",
            "owner",
        )

        extra_kwargs = {"owner": {"read_only": True}}


class LikeSerializer(serializers.ModelSerializer):
    post = serializers.SlugRelatedField(slug_field="content", read_only=True)

    class Meta:
        model = Like
        fields = (
            "id",
            "post",
            "owner",
        )
