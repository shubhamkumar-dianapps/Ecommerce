"""
Profile View

Handles user profile retrieval and updates.
Returns user data with nested profile information based on role.
"""

from rest_framework import generics, permissions
from apps.accounts.serializers.profile import (
    AdminProfileSerializer,
    ShopKeeperProfileSerializer,
    CustomerProfileSerializer,
)
from apps.accounts.models import User
from apps.accounts.services import AuditService


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update user profile.

    GET /api/v1/accounts/profile/
    Returns user data with nested profile based on role.

    PATCH/PUT /api/v1/accounts/profile/
    Update user and profile data.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on user role"""
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return AdminProfileSerializer
        elif user.role == User.Role.SHOPKEEPER:
            return ShopKeeperProfileSerializer
        return CustomerProfileSerializer

    def get_object(self):
        """Return the user object (not profile)"""
        return self.request.user

    def perform_update(self, serializer):
        """Save update and log to audit"""
        user = serializer.save()

        # Log profile update
        AuditService.log_profile_update(
            user=user,
            request=self.request,
            metadata={"updated_fields": list(serializer.validated_data.keys())},
        )
