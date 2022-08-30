from apps.like.models import Like
from apps.post.models import Post
from apps.user.models import User


def create_like(current_user: User, liked_post: Post) -> None:
    Like.objects.create(owner=current_user, post__id=liked_post.id)


def delete_like(current_user: User, liked_post: Post) -> None:
    Like.objects.filter(owner=current_user, post__id=liked_post.id).delete()
