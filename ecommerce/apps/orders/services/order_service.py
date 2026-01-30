"""
Order Service

Business logic for order operations.
"""

from datetime import timedelta
from typing import Tuple, Optional
from django.db import transaction
from django.utils import timezone
from apps.orders.models import Order, ReturnRequest


# Constants
RETURN_WINDOW_DAYS = 7  # Days after delivery when return is allowed


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

    # ==================== RETURN REQUEST METHODS ====================

    @staticmethod
    def can_request_return(order: Order) -> Tuple[bool, str]:
        """
        Check if an order is eligible for return.

        Rules:
        - Order must be DELIVERED
        - Must be within return window (7 days)
        - No existing return request

        Args:
            order: Order instance

        Returns:
            Tuple of (can_return, reason)
        """
        # Check order status
        if order.status != Order.OrderStatus.DELIVERED:
            return False, "Only delivered orders can be returned"

        # Check if return request already exists
        if hasattr(order, "return_request"):
            return False, "Return request already exists for this order"

        # Check return window (7 days from delivery)
        # Using updated_at as proxy for delivery date
        delivery_date = order.updated_at
        return_deadline = delivery_date + timedelta(days=RETURN_WINDOW_DAYS)

        if timezone.now() > return_deadline:
            return False, f"Return window has expired ({RETURN_WINDOW_DAYS} days)"

        return True, "Order is eligible for return"

    @staticmethod
    @transaction.atomic
    def request_return(
        order: Order,
        reason: str,
        description: str = "",
    ) -> Tuple[Optional[ReturnRequest], str]:
        """
        Create a return request for an order.

        Args:
            order: Order instance
            reason: Return reason (from ReturnReason choices)
            description: Additional description

        Returns:
            Tuple of (ReturnRequest or None, message)
        """
        # Check eligibility
        can_return, message = OrderService.can_request_return(order)
        if not can_return:
            return None, message

        # Create return request
        return_request = ReturnRequest.objects.create(
            order=order,
            reason=reason,
            description=description,
            refund_amount=order.total,  # Default to full refund
        )

        return return_request, "Return request submitted successfully"

    @staticmethod
    def get_return_request(order: Order) -> Optional[ReturnRequest]:
        """
        Get return request for an order.

        Args:
            order: Order instance

        Returns:
            ReturnRequest or None
        """
        try:
            return order.return_request
        except ReturnRequest.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def process_refund(return_request: ReturnRequest) -> Tuple[bool, str]:
        """
        Process refund for an approved return request.

        This marks the return as refunded and updates order status.
        Actual payment refund would be handled by payment gateway.

        Args:
            return_request: ReturnRequest instance

        Returns:
            Tuple of (success, message)
        """
        # Check return request status
        if return_request.status not in [
            ReturnRequest.ReturnStatus.APPROVED,
            ReturnRequest.ReturnStatus.RECEIVED,
        ]:
            return False, "Return request must be approved or received first"

        # Update return request status
        return_request.status = ReturnRequest.ReturnStatus.REFUNDED
        return_request.save(update_fields=["status", "updated_at"])

        # Update order status
        order = return_request.order
        order.status = Order.OrderStatus.REFUNDED
        order.payment_status = Order.PaymentStatus.REFUNDED
        order.save(update_fields=["status", "payment_status", "updated_at"])

        # Release inventory
        for item in order.items.all():
            if hasattr(item.product, "inventory"):
                item.product.inventory.release(item.quantity)

        return True, f"Refund of ₹{return_request.refund_amount} processed successfully"
