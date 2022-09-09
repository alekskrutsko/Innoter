from apps.page.models import Page
from apps.post.tasks import notify_follower_about_new_post


def send_email_to_followers(post_data, page_pk) -> None:
    page = Page.objects.prefetch_related('followers').get(pk=page_pk)
    followers_list = page.followers.values_list('email', flat=True)
    notify_follower_about_new_post(page.owner, post_data.get('content'), followers_list)
