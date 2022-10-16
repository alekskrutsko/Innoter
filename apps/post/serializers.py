from rest_framework import serializers

from apps.page.models import Page
from apps.post.models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "page", "content", "reply_to", "created_at", "updated_at")
        extra_kwargs = {
            "page": {"read_only": True},
        }

    def create(self, validated_data):
        kwargs = self.context.get("request").parser_context["kwargs"]
        validated_data["page"] = Page.objects.get(pk=kwargs["page_pk"])

        post = Post.objects.create(**validated_data)

        return post


class UpdatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["content"]


class ListPostSerializer(serializers.ModelSerializer):
    page = serializers.ReadOnlyField(source="page.id")

    class Meta:
        model = Post
        fields = [
            "page",
            "content",
            "reply_to",
            "created_at",
            "updated_at",
        ]
