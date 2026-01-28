"""
Order Service

Business logic for order operations.
"""

from typing import Tuple
from django.db import transaction
from apps.orders.models import Order


class OrderService:
    """Service class for order operations."""

    @staticmethod
    @transaction.atomic
    def cancel_order(order: Order) -> Tuple[bool, str]:
        """
        Cancel an order and release reserved inventory.

        Args:
            order: Order instance to cancel

        Returns:
            Tuple of (success, message)
        """
        # Check if order can be cancelled
        non_cancellable_statuses = [
            Order.OrderStatus.DELIVERED,
            Order.OrderStatus.CANCELLED,
            Order.OrderStatus.REFUNDED,
        ]

        if order.status in non_cancellable_statuses:
            return False, f"Cannot cancel order with status: {order.status}"

        # Release reserved inventory for each item
        for item in order.items.all():
            if hasattr(item.product, "inventory"):
                item.product.inventory.release(item.quantity)

        # Update order status
        order.status = Order.OrderStatus.CANCELLED
        order.save(update_fields=["status", "updated_at"])

        return True, "Order cancelled successfully"

    @staticmethod
    def get_user_orders(user, status: str = None):
        """
        Get orders for a user with optional status filter.

        Args:
            user: User instance
            status: Optional status filter

        Returns:
            QuerySet of orders
        """
        queryset = Order.objects.filter(user=user).prefetch_related("items")

        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by("-created_at")

    @staticmethod
    def can_cancel_order(order: Order) -> bool:
        """
        Check if an order can be cancelled.

        Args:
            order: Order instance

        Returns:
            bool: True if order can be cancelled
        """
        non_cancellable_statuses = [
            Order.OrderStatus.DELIVERED,
            Order.OrderStatus.CANCELLED,
            Order.OrderStatus.REFUNDED,
            Order.OrderStatus.SHIPPED,
        ]
        return order.status not in non_cancellable_statuses
