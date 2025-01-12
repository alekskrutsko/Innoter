from datetime import datetime, timedelta

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.page.models import Page
from apps.tag.models import Tag
from apps.user.models import User
from apps.user.services import generate_file_name, get_presigned_url, is_allowed_file_extension


def time_converter(time: list):
    int_time = int(time[1])

    time_dict = {
        "minutes": timedelta(minutes=int_time),
        "hours": timedelta(hours=int_time),
        "days": timedelta(days=int_time),
    }

    return time_dict[time[0].lower()]


def set_to_private(request, pk):
    user = request.user
    page = get_object_or_404(
        Page,
        Q(is_permanently_blocked=False) & (Q(unblock_date__isnull=True) | Q(unblock_date__lt=datetime.now())),
        pk=pk,
        owner=user,
    )
    page.is_private = True
    page.save()
    return True, status.HTTP_200_OK


def set_to_public(request, pk):
    user = request.user
    page = get_object_or_404(
        Page,
        Q(is_permanently_blocked=False) & (Q(unblock_date__isnull=True) | Q(unblock_date__lt=datetime.now())),
        pk=pk,
        owner=user,
    )
    page.is_private = False
    page.save()
    return True, status.HTTP_200_OK


def get_unblocked_pages() -> Page:
    pages = Page.objects.filter(
        Q(is_permanently_blocked=False) & (Q(unblock_date__isnull=True) | Q(unblock_date__lt=datetime.now())),
    ).order_by("id")
    return pages


def get_blocked_pages() -> Page:
    return Page.objects.filter(
        Q(is_permanently_blocked=True) | (Q(unblock_date__isnull=False) & Q(unblock_date__gt=datetime.now()))
    ).order_by("id")


def get_page_followers(page_pk: int) -> Page:
    return get_object_or_404(Page, pk=page_pk).followers.all().order_by("id")


def get_page_follow_requests(page_pk: int) -> Response:
    return get_object_or_404(Page, pk=page_pk).follow_requests.all().order_by("id")


def follow_page(user: User, page_pk: int) -> tuple:
    page = get_object_or_404(Page, pk=page_pk)
    is_user_follower = page.followers.filter(id=user.pk).exists()
    if page.is_private and not is_user_follower:
        page.follow_requests.add(user)
        return True, is_user_follower
    elif not is_user_follower:
        page.followers.add(user)
    return False, is_user_follower


def unfollow_page(user: User, page_pk: int) -> tuple:
    page = get_object_or_404(Page, pk=page_pk)
    is_user_follower = page.followers.filter(id=user.pk).exists()
    page.followers.remove(user)
    return page.owner.pk, is_user_follower


def accept_follow_request(follower_email: str, page_pk: int) -> bool:
    page = get_object_or_404(Page, pk=page_pk)
    potential_follower = get_object_or_404(User, email=follower_email)
    is_follow_request = page.follow_requests.filter(pk=potential_follower.pk).exists()
    page.followers.add(potential_follower)
    page.follow_requests.remove(potential_follower)
    return is_follow_request


def deny_follow_request(follower_email: str, page_pk: int) -> None:
    page = get_object_or_404(Page, pk=page_pk)
    potential_follower = get_object_or_404(User, email=follower_email)
    page.follow_requests.remove(potential_follower)


def accept_all_follow_requests(page_pk: int) -> int:
    page = get_object_or_404(Page, pk=page_pk)
    follow_requests = page.follow_requests.all()
    follow_requests_number = 0
    if follow_requests:
        for potential_follower in follow_requests:
            follow_requests_number += 1
            page.followers.add(potential_follower)
            page.follow_requests.remove(potential_follower)
    return follow_requests_number


def deny_all_follow_requests(page_pk: int) -> None:
    page = get_object_or_404(Page, pk=page_pk)
    follow_requests = page.follow_requests.all()
    if follow_requests:
        for potential_follower in follow_requests:
            page.follow_requests.remove(potential_follower)


def get_page_tags(page_pk: int) -> Tag:
    page = get_object_or_404(Page, pk=page_pk)
    return page.tags.all()


def add_tag_to_page(tag_name: str, page_pk: int) -> None:
    page = get_object_or_404(Page, pk=page_pk)
    tag = get_object_or_404(Tag, name=tag_name)
    page.tags.add(tag)


def remove_tag_from_page(tag_name: str, page_pk: int) -> None:
    page = get_object_or_404(Page, pk=page_pk)
    tag = get_object_or_404(Tag, name=tag_name)
    page.tags.remove(tag)


def upload_image_to_s3(request, pk):
    image = request.FILES["image"]
    if not is_allowed_file_extension(file_path=image.name):
        raise ValidationError()

    page = get_object_or_404(Page, pk=pk)
    key = generate_file_name(file_path=image.name, key=page.uuid, is_user_image=False)

    presigned_url = get_presigned_url(image=image, key=key)

    page.image = presigned_url
    page.save()

    return presigned_url
