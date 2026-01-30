"""
Customer Permission Classes

Permission classes for customer access control.
"""

from rest_framework.permissions import BasePermission
from apps.accounts.models import User


class IsCustomer(BasePermission):
    """
    Only allow access to customer users.

    Usage:
        permission_classes = [IsAuthenticated, IsCustomer]
    """

    message = "Only customers can access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.CUSTOMER
        )


# Note: IsOrderOwner and IsReviewOwner permissions are handled via:
# - OrderViewSet.get_queryset() filters by user automatically
# - reviews/permissions.py has IsReviewOwnerOrReadOnly
