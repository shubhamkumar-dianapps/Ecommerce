import uuid
from django.db import models
from .user import User


class SocialAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="social_accounts"
    )
    provider = models.CharField(max_length=50)  # e.g., 'google', 'facebook'
    uid = models.CharField(max_length=255)
    extra_data = models.JSONField(default=dict)

    class Meta:
        unique_together = ("provider", "uid")

    def __str__(self):
        return f"{self.user.email} - {self.provider}"
