from rest_framework import serializers


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification with token"""

    token = serializers.UUIDField(required=True)


class ResendVerificationSerializer(serializers.Serializer):
    """Serializer for resending verification email"""

    email = serializers.EmailField(required=True)
