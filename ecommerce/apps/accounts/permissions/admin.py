"""
Admin Permission Classes

Permission classes for admin-only access.
"""

from rest_framework.permissions import BasePermission
from apps.accounts.models import User


class IsAdmin(BasePermission):
    """
    Only allow access to admin users.

    Usage:
        permission_classes = [IsAuthenticated, IsAdmin]
    """

    message = "Only administrators can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.ADMIN
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Allow read access to everyone, write access only to admins.

    Usage:
        permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    """

    message = "Only administrators can modify this resource."

    def has_permission(self, request, view):
        # Read permissions for any authenticated request
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return request.user and request.user.is_authenticated

        # Write permissions only for admin
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.ADMIN
        )
