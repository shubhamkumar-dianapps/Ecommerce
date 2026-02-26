"""
Email Change Token Model

Stores tokens for email change verification.
"""

import uuid
from datetime import timedelta
from django.db import models
from django.utils import timezone
from .user import User


class EmailChangeToken(models.Model):
    """
    Model to store email change verification tokens.

    When a user wants to change their email:
    1. Create token with new_email
    2. Send verification email to new_email
    3. User clicks link -> verify new email is valid
    4. Update user's email and mark token as used
    """

    EXPIRY_HOURS = 24

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="email_change_tokens"
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    current_email = models.EmailField(help_text="User's email at time of request")
    new_email = models.EmailField(help_text="The new email address to verify")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["token", "is_used"]),
            models.Index(fields=["user", "is_used"]),
            models.Index(fields=["new_email"]),
        ]

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=self.EXPIRY_HOURS)
        # Store current email at time of request
        if not self.current_email:
            self.current_email = self.user.email
        super().save(*args, **kwargs)

    def is_valid(self) -> bool:
        """Check if token is still valid."""
        return (
            not self.is_used
            and timezone.now() < self.expires_at
            and self.user.email == self.current_email  # Email hasn't changed since
        )

    def mark_as_used(self) -> None:
        """Mark token as used."""
        self.is_used = True
        self.save(update_fields=["is_used"])

    def __str__(self):
        return f"Email change token: {self.current_email} -> {self.new_email}"
