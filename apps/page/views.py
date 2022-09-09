from datetime import datetime

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from apps.page.models import Page
from apps.page.permissions import IsAdminOrModerator, IsBlockedPage, IsPageOwner, IsPrivatePage
from apps.page.serializers import (
    AdminOrModerPageSerializer,
    FollowerSerializer,
    FollowersListSerializer,
    PageListSerializer,
    UserPageSerializer,
)
from apps.page.services import (
    accept_all_follow_requests,
    accept_follow_request,
    add_tag_to_page,
    deny_all_follow_requests,
    deny_follow_request,
    follow_page,
    get_blocked_pages,
    get_page_follow_requests,
    get_page_followers,
    get_page_tags,
    get_unblocked_pages,
    remove_tag_from_page,
    set_to_private,
    set_to_public,
    time_converter,
    unfollow_page,
    upload_image_to_s3,
)
from apps.tag.serializers import TagPageSerializer, TagSerializer
from innotter.basic_mixin import GetPermissionsMixin, GetSerializerMixin


class PagesListViewSet(GetPermissionsMixin, ModelViewSet):
    serializer_class = UserPageSerializer
    queryset = Page.objects.all()
    permission_classes = {
        "create": (IsAuthenticated,),
        "retrieve": (
            IsAuthenticated,
            (~IsPrivatePage | IsPageOwner | IsAdminOrModerator),
            IsBlockedPage,
        ),
        "update": (
            IsAuthenticated,
            IsPageOwner,
            IsBlockedPage,
        ),
        "destroy": (
            IsAuthenticated,
            (IsPageOwner | IsAdminOrModerator),
            IsBlockedPage,
        ),
        "list": (
            IsAuthenticated,
            IsAdminOrModerator,
        ),
        "block": (
            IsAuthenticated,
            IsAdminOrModerator,
        ),
        "unblock": (
            IsAuthenticated,
            IsAdminOrModerator,
        ),
        "blocked": (
            IsAuthenticated,
            IsAdminOrModerator,
        ),
        "followers": (IsAuthenticated, ~IsBlockedPage),
        "follow": (IsAuthenticated, ~IsBlockedPage),
        "unfollow": (IsAuthenticated, ~IsBlockedPage),
    }
    serializer_classes = {
        "list": PageListSerializer,
        "blocked": PageListSerializer,
        "followers": FollowersListSerializer,
    }
    detail_serializer_classes = {
        "admin": AdminOrModerPageSerializer,
        "moderator": AdminOrModerPageSerializer,
        "user": UserPageSerializer,
    }

    @action(detail=True, methods=("patch",))
    def block(self, request, *args, **kwargs):
        page = request.data.get(
            "page",
        )

        page_model = Page.objects.get(pk=kwargs["pk"])
        if not page.get("permanent_block"):
            time = page["block_time"].split()
            page_model.unblock_date = datetime.now() + time_converter(time)
        else:
            page_model.is_permanently_blocked = True

        page_model.save()

        return Response(UserPageSerializer(page_model).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=("patch",))
    def unblock(self, request, *args, **kwargs):
        page = request.data.get(
            "page",
        )

        page_model = Page.objects.get(pk=kwargs["pk"])
        if not page.get("permanent_block"):
            page_model.unblock_date = datetime.now()
        else:
            page_model.is_permanent_blocked = False

        page_model.save()

        return Response(UserPageSerializer(page_model).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="blocked")
    def blocked(self, request):
        all_blocked_pages = get_blocked_pages()
        serializer = self.get_serializer(all_blocked_pages, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="followers")
    def followers(self, request, pk=None):
        all_page_followers = get_page_followers(page_pk=pk)
        serializer = self.get_serializer(all_page_followers, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="follow")
    def follow(self, request, pk=None):
        is_private, page_owner_id, is_follower = follow_page(user=self.request.user, page_pk=pk)
        if not is_private:
            return Response(
                {"detail": "You have subscribed to the page or you are already a subscriber."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": "You have applied for a subscription."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="unfollow")
    def unfollow(self, request, pk=None):
        unfollow_page(user=self.request.user, page_pk=pk)
        return Response(
            {"detail": "You have unsubscribed from the page or have already been unsubscribed."},
            status=status.HTTP_200_OK,
        )

    def get_serializer_class(self):
        if self.action in (
            "retrieve",
            "update",
            "partial_update",
            "follow",
            "unfollow",
        ):
            return self.detail_serializer_classes.get(self.request.user.role)
        return self.serializer_classes.get(self.action)


class CurrentUserPagesViewSet(
    GetSerializerMixin,
    GetPermissionsMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    permission_classes = {
        "create": (IsAuthenticated,),
        "retrieve": (
            IsAuthenticated,
            (~IsPrivatePage | IsPageOwner | IsAdminOrModerator),
            IsBlockedPage,
        ),
        "update": (
            IsAuthenticated,
            IsPageOwner,
            IsBlockedPage,
        ),
        "destroy": (
            IsAuthenticated,
            (IsPageOwner | IsAdminOrModerator),
            IsBlockedPage,
        ),
        "list": (
            IsAuthenticated,
            IsBlockedPage,
        ),
        "set_private": (
            IsAuthenticated,
            IsPageOwner,
            IsBlockedPage,
        ),
        "set_public": (
            IsAuthenticated,
            IsPageOwner,
            IsBlockedPage,
        ),
        "follow_requests": (IsAuthenticated, (IsPageOwner | IsAdminOrModerator)),
        "followers": (
            IsAuthenticated,
            IsBlockedPage,
            (IsPageOwner | IsAdminOrModerator),
        ),
    }

    serializer_classes = {
        "list": PageListSerializer,
        "create": PageListSerializer,
        "follow_requests": FollowersListSerializer,
        "all_follow_requests": FollowersListSerializer,
        "followers": FollowersListSerializer,
        "deny_follow_request": FollowerSerializer,
        "accept_follow_request": FollowerSerializer,
        "tags": TagSerializer,
        "add_tag_to_page": TagPageSerializer,
        "remove_tag_from_page": TagPageSerializer,
        "set_private": PageListSerializer,
        "set_public": PageListSerializer,
    }

    def perform_update(self, serializer):
        image = serializer.validated_data["image"]
        page_id = serializer.validated_data["id"]
        serializer.validated_data["image"] = upload_image_to_s3(file_path=image, page_id=page_id)
        serializer.save()

    @action(detail=True, methods=["get"], url_path="followers")
    def followers(self, request, pk=None):
        all_page_followers = get_page_followers(page_pk=pk)
        serializer = self.get_serializer(all_page_followers, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="follow-requests")
    def page_follow_requests(self, request, pk=None):
        page_follow_requests = get_page_follow_requests(page_pk=pk)
        serializer = self.get_serializer(page_follow_requests, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="accept")
    def accept_follow_request(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        accept_follow_request(follower_email=email, page_pk=pk)
        return Response(
            {"detail": "You have successfully accepted user to followers or user is already your follower."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="deny")
    def deny_follow_request(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        deny_follow_request(follower_email=email, page_pk=pk)
        return Response(
            {"detail": "You have successfully removed user from followers or user is already removed."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="accept-all")
    def accept_all_follow_requests(self, request, pk=None):
        accept_all_follow_requests(page_pk=pk)
        return Response(
            {"detail": "You have successfully accepted all follow requests."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="deny-all")
    def deny_all_follow_requests(self, request, pk=None):
        deny_all_follow_requests(page_pk=pk)
        return Response(
            {"detail": "You have successfully denied all follow requests."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"], url_path="tags")
    def tags(self, request, pk=None):
        page_tags = get_page_tags(page_pk=pk)
        serializer = self.get_serializer(page_tags, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="add-tag")
    def add_tag_to_page(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tag_name = serializer.validated_data["name"]
        add_tag_to_page(tag_name=tag_name, page_pk=pk)
        return Response(
            {"detail": "You have successfully added tag to page or it's already added."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["delete"], url_path="remove-tag")
    def remove_tag_from_page(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tag_name = serializer.validated_data["name"]
        remove_tag_from_page(tag_name=tag_name, page_pk=pk)
        return Response(
            {"detail": "You have successfully removed tag from page or it's already removed."},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["put"])
    def set_private(self, request, pk):
        data, status = set_to_private(request, pk)
        return Response(data=data, status=status)

    @action(detail=True, methods=["put"])
    def set_public(self, request, pk):
        data, status = set_to_public(request, pk)
        return Response(data=data, status=status)

    @action(
        detail=True,
        methods=("put",),
    )
    def set_avatar(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        page_id = serializer.validated_data["id"]
        image = serializer.validated_data["image"]
        serializer.validated_data["image"] = upload_image_to_s3(file_path=image, page_id=page_id)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        if self.request.user.role in ("admin", "moderator"):
            return Page.objects.all().order_by("id")
        return get_unblocked_pages()
