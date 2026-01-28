"""
Reviews App Permissions

Custom permission classes for review and reply access control.
"""

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView
from apps.accounts.models import User


class IsReviewOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow review owners to edit their reviews.

    - Read access: Everyone
    - Write access: Review owner only
    """

    def has_object_permission(self, request: Request, view: APIView, obj: any) -> bool:
        """Check if user can access the review"""
        # Allow read access to anyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write access only for review owner
        return obj.user == request.user


class CanReplyToReview(permissions.BasePermission):
    """
    Permission for users who can reply to reviews.

    Allowed users:
    - Product owner (shopkeeper who owns the product)
    - Verified purchaser (customer who has purchased the product)
    - Admin
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Check if user can reply to reviews"""
        if not request.user.is_authenticated:
            return False

        # Admin can always reply
        if request.user.role == User.Role.ADMIN:
            return True

        # For other users, we need to check object-level permission
        # Allow the request to proceed, actual check done in has_object_permission
        return True

    def has_object_permission(self, request: Request, view: APIView, obj) -> bool:
        """Check if user can reply to this specific review"""
        # Admin can always reply
        if request.user.role == User.Role.ADMIN:
            return True

        review = obj
        product = review.product

        # Product owner can reply
        if product.shopkeeper == request.user:
            return True

        # Verified purchaser can reply (customer who has ordered this product)
        if request.user.role == User.Role.CUSTOMER:
            from apps.orders.models import Order, OrderItem

            # Check if user has a delivered order containing this product
            has_purchased = OrderItem.objects.filter(
                order__user=request.user,
                order__status=Order.OrderStatus.DELIVERED,
                product=product,
            ).exists()

            return has_purchased

        return False


class IsReplyOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to only allow reply owners to edit their replies.

    - Read access: Everyone
    - Write access: Reply owner only
    """

    def has_object_permission(self, request: Request, view: APIView, obj: any) -> bool:
        """Check if user can access the reply"""
        # Allow read access to anyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write access only for reply owner
        return obj.user == request.user
