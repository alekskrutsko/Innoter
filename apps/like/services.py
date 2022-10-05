from apps.like.models import Like
from apps.post.models import Post
from apps.producer import publish
from apps.user.models import User


def create_like(current_user: User, liked_post: Post) -> None:
    Like.objects.create(owner=current_user, post=liked_post)
    publish("like_created", liked_post.page.pk)


def delete_like(current_user: User, liked_post: Post) -> None:
    Like.objects.filter(owner=current_user, post=liked_post).delete()
    publish("like_deleted", liked_post.page.pk)
