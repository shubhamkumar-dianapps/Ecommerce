"""
Base Permission Classes

Common permission classes used across apps.
"""

from rest_framework.permissions import BasePermission


class IsEmailVerified(BasePermission):
    """
    Only allow access to users with verified email.

    Use with IsAuthenticated:
        permission_classes = [IsAuthenticated, IsEmailVerified]
    """

    message = "Please verify your email to access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.email_verified
        )


class IsActiveUser(BasePermission):
    """
    Only allow access to active users.

    Typically combined with IsAuthenticated.
    """

    message = "Your account has been deactivated."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active
