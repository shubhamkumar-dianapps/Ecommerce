from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.accounts.models import User


class LoginSerializer(TokenObtainPairSerializer):
    """
    Custom login serializer with specific error messages.

    Provides different error messages for:
    - User not found (email doesn't exist)
    - Invalid password (email exists but wrong password)
    - Inactive account
    """

    def validate(self, attrs):
        email = attrs.get("email", "")
        password = attrs.get("password", "")

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "No account found with this email address."}
            )

        # Check if account is active
        if not user.is_active:
            raise serializers.ValidationError(
                {"email": "This account has been deactivated. Please contact support."}
            )

        # Check password
        authenticated_user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )

        if authenticated_user is None:
            raise serializers.ValidationError(
                {"password": "Invalid password. Please try again."}
            )

        # Call parent validate for token generation
        data = super().validate(attrs)
        data["user"] = {
            "email": self.user.email,
            "role": self.user.role,
            "id": self.user.id,
        }
        return data
