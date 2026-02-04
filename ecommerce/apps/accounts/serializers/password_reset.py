"""
Password Reset Serializers

Serializers for password reset flow.
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.accounts.models import User


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset.

    Takes email and sends reset link if user exists.
    Always returns success to prevent email enumeration.
    """

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming password reset with new password.
    """

    token = serializers.UUIDField()
    new_password = serializers.CharField(
        min_length=8,
        write_only=True,
        validators=[validate_password],
    )
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )
        return attrs


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
