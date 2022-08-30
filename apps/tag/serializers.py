from rest_framework import serializers

from apps.tag.models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")


class TagPageSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=30, required=True)
    class Meta:
        model = Tag
        fields = ("name",)
