"""
Password Reset Serializers

Serializers for password reset flow.
"""

from rest_framework import serializers
from apps.accounts.models import User
from apps.accounts.fields import PasswordField, PasswordConfirmField
from apps.accounts.mixins import PasswordConfirmationMixin


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset.

    Takes email and sends reset link if user exists.
    Always returns success to prevent email enumeration.
    """

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer, PasswordConfirmationMixin):
    """
    Serializer for confirming password reset with new password.
    """

    password_field = "new_password"
    confirm_field = "confirm_password"

    token = serializers.UUIDField()
    new_password = PasswordField()
    confirm_password = PasswordConfirmField()


class EmailChangeRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting an email change.

    Takes new email and current password for security.
    """

    new_email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_new_email(self, value):
        # Check if email is already in use
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use")
        return value

    def validate(self, attrs):
        # Validate current password
        request = self.context.get("request")
        if not request.user.check_password(attrs["password"]):
            raise serializers.ValidationError(
                {"password": "Current password is incorrect"}
            )
        return attrs


class EmailChangeConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming email change.
    """

    token = serializers.UUIDField()
