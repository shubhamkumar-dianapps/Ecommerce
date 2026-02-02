"""
Test Factories for Orders App

Reusable factories for creating test orders and order items.
"""

from decimal import Decimal
from apps.orders.models import Order, OrderItem
from apps.accounts.tests.factories import UserFactory
from apps.addresses.tests.factories import AddressFactory
from apps.products.tests.factories import ProductFactory


class OrderFactory:
    """Factory for creating test orders."""

    _counter = 0

    @classmethod
    def _get_unique_id(cls):
        cls._counter += 1
        return cls._counter

    @classmethod
    def create_order(
        cls,
        user=None,
        shipping_address=None,
        subtotal: Decimal = Decimal("100.00"),
        tax: Decimal = Decimal("10.00"),
        shipping_cost: Decimal = Decimal("5.00"),
        status: str = "PENDING",
        payment_status: str = "PENDING",
    ) -> Order:
        """Create a test order."""
        if user is None:
            user = UserFactory.create_customer()
        if shipping_address is None:
            shipping_address = AddressFactory.create_address(user=user)

        total = subtotal + tax + shipping_cost

        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            subtotal=subtotal,
            tax=tax,
            shipping_cost=shipping_cost,
            total=total,
            status=status,
            payment_status=payment_status,
        )
        return order

    @classmethod
    def create_order_with_items(
        cls,
        user=None,
        num_items: int = 2,
        **kwargs,
    ) -> Order:
        """Create a test order with items."""
        order = cls.create_order(user=user, **kwargs)

        for i in range(num_items):
            product = ProductFactory.create_product()
            OrderItemFactory.create_order_item(
                order=order,
                product=product,
                quantity=i + 1,
            )

        return order


class OrderItemFactory:
    """Factory for creating test order items."""

    @classmethod
    def create_order_item(
        cls,
        order: Order = None,
        product=None,
        quantity: int = 1,
        unit_price: Decimal = None,
    ) -> OrderItem:
        """Create a test order item."""
        if order is None:
            order = OrderFactory.create_order()
        if product is None:
            product = ProductFactory.create_product()
        if unit_price is None:
            unit_price = product.price

        return OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_sku=product.sku,
            unit_price=unit_price,
            quantity=quantity,
        )
