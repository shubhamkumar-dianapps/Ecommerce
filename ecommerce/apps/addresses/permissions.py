"""
Address Permissions

Custom permission classes for address operations.
"""

from rest_framework import permissions
from typing import Any
from django.http import HttpRequest
from apps.addresses.models import Address


class IsAddressOwner(permissions.BasePermission):
    """
    Permission to only allow owners to view/edit their addresses.

    Used to ensure users can only access their own addresses.
    """

    message = "You do not have permission to access this address"

    def has_object_permission(
        self, request: HttpRequest, view: Any, obj: Address
    ) -> bool:
        """
        Check if user owns the address.

        Args:
            request: HTTP request
            view: View being accessed
            obj: Address object

        Returns:
            bool: True if user owns address, False otherwise
        """
        return obj.user == request.user
