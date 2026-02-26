import uuid
from django.db import models
from .user import User


class AuditLog(models.Model):
    """
    Model for logging security-related events.
    Tracks authentication attempts, password changes, and other critical actions.
    """

    class Action(models.TextChoices):
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        FAILED_LOGIN = "FAILED_LOGIN", "Failed Login"
        PASSWORD_CHANGE = "PASSWORD_CHANGE", "Password Change"
        PASSWORD_RESET_REQUEST = "PASSWORD_RESET_REQUEST", "Password Reset Request"
        PASSWORD_RESET_COMPLETE = "PASSWORD_RESET_COMPLETE", "Password Reset Complete"
        EMAIL_VERIFICATION = "EMAIL_VERIFICATION", "Email Verification"
        EMAIL_CHANGE_REQUEST = "EMAIL_CHANGE_REQUEST", "Email Change Request"
        EMAIL_CHANGE_COMPLETE = "EMAIL_CHANGE_COMPLETE", "Email Change Complete"
        PHONE_CHANGE = "PHONE_CHANGE", "Phone Number Change"
        PROFILE_UPDATE = "PROFILE_UPDATE", "Profile Update"
        ACCOUNT_CREATED = "ACCOUNT_CREATED", "Account Created"
        ACCOUNT_DEACTIVATED = "ACCOUNT_DEACTIVATED", "Account Deactivated"
        ACCOUNT_REACTIVATED = "ACCOUNT_REACTIVATED", "Account Reactivated"
        SESSION_REVOKED = "SESSION_REVOKED", "Session Revoked"
        TWO_FACTOR_ENABLED = "TWO_FACTOR_ENABLED", "Two-Factor Authentication Enabled"
        TWO_FACTOR_DISABLED = (
            "TWO_FACTOR_DISABLED",
            "Two-Factor Authentication Disabled",
        )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50, choices=Action.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "action", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
        ]

    def __str__(self):
        user_email = self.user.email if self.user else "Unknown"
        return f"{self.action} by {user_email} at {self.created_at}"
