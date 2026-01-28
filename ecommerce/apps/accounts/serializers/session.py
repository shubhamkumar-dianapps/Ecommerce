from rest_framework import serializers
from apps.accounts.models import UserSession


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for user session details"""

    class Meta:
        model = UserSession
        fields = [
            "id",
            "ip_address",
            "user_agent",
            "created_at",
            "last_activity",
            "is_active",
        ]
        read_only_fields = fields


class RevokeSessionSerializer(serializers.Serializer):
    """Serializer for session revocation"""

    session_id = serializers.UUIDField(required=True)
