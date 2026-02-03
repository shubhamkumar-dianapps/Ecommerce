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

    Optimized to minimize database queries.
    """

    def validate(self, attrs):
        email = attrs.get("email", "")
        password = attrs.get("password", "")

        # Check if user exists (Query 1)
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

        # Check password directly (avoids authenticate() extra query)
        if not user.check_password(password):
            raise serializers.ValidationError(
                {"password": "Invalid password. Please try again."}
            )

        # Set user for parent class to avoid another query
        self.user = user

        # Call parent for token generation (will reuse self.user)
        data = super().validate(attrs)
        data["user"] = {
            "email": self.user.email,
            "role": self.user.role,
            "id": self.user.id,
        }
        return data
