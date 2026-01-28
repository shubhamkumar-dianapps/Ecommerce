"""
Products Permissions

Custom permission classes for products app.
"""

from typing import Any
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView
from apps.accounts.models import User
from apps.products import constants


class IsShopkeeperOrReadOnly(permissions.BasePermission):
    """
    Permission: Allow read access to anyone, write access only to verified shopkeepers.

    - Safe methods (GET, HEAD, OPTIONS): Anyone ✅
    - Unsafe methods (POST, PUT, PATCH, DELETE): Verified shopkeepers only ✅
    """

    message = constants.NOT_SHOPKEEPER

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user has permission to access this view.

        Args:
            request: HTTP request
            view: View being accessed

        Returns:
            bool: True if allowed, False otherwise
        """
        # Allow read-only for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write operations, user must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # User must be a shopkeeper
        if request.user.role != User.Role.SHOPKEEPER:
            self.message = constants.NOT_SHOPKEEPER
            return False

        # Shopkeeper must be verified
        if not hasattr(request.user, "shopkeeperprofile"):
            return False

        if not request.user.shopkeeperprofile.is_verified:
            self.message = constants.SHOPKEEPER_NOT_VERIFIED
            return False

        return True


class IsProductOwner(permissions.BasePermission):
    """
    Permission: Only the shopkeeper who created the product can edit/delete it.

    Used for object-level permissions on Product instances.
    """

    message = constants.NOT_PRODUCT_OWNER

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """
        Check if user has permission to access this specific product.

        Args:
            request: HTTP request
            view: View being accessed
            obj: Product instance

        Returns:
            bool: True if allowed, False otherwise
        """
        # Allow read-only for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write operations, check ownership
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if product has a shopkeeper field
        if not hasattr(obj, "shopkeeper"):
            return False

        # User must be the product owner
        return obj.shopkeeper == request.user


class IsVerifiedShopkeeper(permissions.BasePermission):
    """
    Permission: User must be a verified shopkeeper.

    Used for actions that require verified shopkeeper status.
    """

    message = constants.SHOPKEEPER_NOT_VERIFIED

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Check if user is a verified shopkeeper.

        Args:
            request: HTTP request
            view: View being accessed

        Returns:
            bool: True if verified shopkeeper, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.role != User.Role.SHOPKEEPER:
            self.message = constants.NOT_SHOPKEEPER
            return False

        if not hasattr(request.user, "shopkeeperprofile"):
            return False

        return request.user.shopkeeperprofile.is_verified
