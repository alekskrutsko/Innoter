from django.db import models


class Like(models.Model):
    post = models.ForeignKey(
        "post.Post",
        on_delete=models.SET_NULL,
        related_name="likes",
        blank=True,
        null=True,
    )
    owner = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="likes",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"like_{self.id}"
