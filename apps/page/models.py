from datetime import datetime

from django.db import models
from pytz import UTC


class Page(models.Model):
    name = models.CharField(max_length=80)
    uuid = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    tags = models.ManyToManyField('tag.Tag', related_name='pages')

    owner = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='pages')
    followers = models.ManyToManyField('user.User', related_name='follows')

    image_url = models.URLField(null=True, blank=True)

    is_private = models.BooleanField(default=False)
    follow_requests = models.ManyToManyField('user.User', related_name='requests')

    unblock_date = models.DateTimeField(null=True, blank=True)
    is_permanently_blocked = models.BooleanField(default=False)

    def is_temporary_blocked(self):
        if not self.unblock_date:
            return True

        utc_now = datetime.utcnow().replace(tzinfo=UTC)
        utc_unblock_date = self.unblock_date.replace(tzinfo=UTC)
        return utc_now > utc_unblock_date
