import boto3
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.user.models import User
from innotter import settings


def upload_photo_to_s3(request):
    user = request.user
    image = request.FILES["image"]
    if not is_allowed_file_extension(file_path=image.name):
        raise ValidationError()

    key = generate_file_name(file_path=image.name, key=user.email, is_user_image=True)

    presigned_url = get_presigned_url(image=image, key=key)

    us = get_object_or_404(User, pk=user.pk)
    us.image_s3_path = presigned_url
    us.save()

    return presigned_url


def get_presigned_url(image, key: str) -> str:
    s3_client = boto3.client(
        "s3",
        endpoint_url=settings.AWS_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    s3_client.put_object(Body=image, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
    presigned_url = s3_client.generate_presigned_url(
        'get_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': key}, ExpiresIn=3600
    )
    return presigned_url


def is_allowed_file_extension(file_path: str) -> bool:
    return file_path.split(".")[-1] in settings.ALLOWED_FILE_EXTENSIONS


def generate_file_name(file_path: str, key: str, is_user_image: bool) -> str:
    extension = file_path.split(".")[-1]
    prefix_folder = "users" if is_user_image else "pages"
    return f"{prefix_folder}/{key}.{extension}"
