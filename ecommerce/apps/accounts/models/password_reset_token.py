"""
Password Reset Token Model

Stores tokens for password reset requests.
"""

import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
from .user import User


class PasswordResetToken(models.Model):
    """
    Model to store password reset tokens.
    Tokens expire after 1 hour for security.
    """

    # 1 hour expiry for password reset (more secure than email verification)
    EXPIRY_HOURS = 1

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="password_reset_tokens"
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["token", "is_used"]),
            models.Index(fields=["user", "is_used"]),
        ]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=self.EXPIRY_HOURS)
        super().save(*args, **kwargs)

    def is_valid(self) -> bool:
        """Check if token is still valid (not used and not expired)."""
        return not self.is_used and timezone.now() < self.expires_at

    def mark_as_used(self) -> None:
        """Mark token as used."""
        self.is_used = True
        self.save(update_fields=["is_used"])

    def __str__(self):
        return f"Password reset token for {self.user.email}"
