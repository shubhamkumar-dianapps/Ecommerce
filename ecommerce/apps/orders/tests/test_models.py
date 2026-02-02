"""
Tests for Order Models

Comprehensive tests for Order and OrderItem models.
"""

from decimal import Decimal
from django.test import TestCase
from apps.orders.tests.factories import OrderFactory, OrderItemFactory
from apps.accounts.tests.factories import UserFactory
from apps.products.tests.factories import ProductFactory


class OrderModelTest(TestCase):
    """Test cases for Order model."""

    def setUp(self):
        self.user = UserFactory.create_customer()

    def test_create_order(self):
        """Test creating an order."""
        order = OrderFactory.create_order(user=self.user)

        self.assertEqual(order.user, self.user)
        self.assertIsNotNone(order.order_number)
        self.assertEqual(order.status, "PENDING")
        self.assertEqual(order.payment_status, "PENDING")

    def test_order_number_auto_generated(self):
        """Test that order number is auto-generated."""
        order = OrderFactory.create_order()

        self.assertTrue(order.order_number.startswith("ORD-"))
        self.assertEqual(len(order.order_number), 14)  # ORD- + 10 chars

    def test_order_number_unique(self):
        """Test that order numbers are unique."""
        order1 = OrderFactory.create_order()
        order2 = OrderFactory.create_order()

        self.assertNotEqual(order1.order_number, order2.order_number)

    def test_order_str_representation(self):
        """Test string representation of order."""
        order = OrderFactory.create_order(user=self.user)

        str_repr = str(order)
        self.assertIn(order.order_number, str_repr)
        self.assertIn(self.user.email, str_repr)

    def test_order_totals(self):
        """Test order total calculation."""
        order = OrderFactory.create_order(
            subtotal=Decimal("100.00"),
            tax=Decimal("10.00"),
            shipping_cost=Decimal("5.00"),
        )

        self.assertEqual(order.total, Decimal("115.00"))

    def test_order_statuses(self):
        """Test different order statuses."""
        pending = OrderFactory.create_order(status="PENDING")
        confirmed = OrderFactory.create_order(status="CONFIRMED")
        shipped = OrderFactory.create_order(status="SHIPPED")
        delivered = OrderFactory.create_order(status="DELIVERED")
        cancelled = OrderFactory.create_order(status="CANCELLED")

        self.assertEqual(pending.status, "PENDING")
        self.assertEqual(confirmed.status, "CONFIRMED")
        self.assertEqual(shipped.status, "SHIPPED")
        self.assertEqual(delivered.status, "DELIVERED")
        self.assertEqual(cancelled.status, "CANCELLED")

    def test_payment_statuses(self):
        """Test different payment statuses."""
        pending = OrderFactory.create_order(payment_status="PENDING")
        paid = OrderFactory.create_order(payment_status="PAID")
        failed = OrderFactory.create_order(payment_status="FAILED")

        self.assertEqual(pending.payment_status, "PENDING")
        self.assertEqual(paid.payment_status, "PAID")
        self.assertEqual(failed.payment_status, "FAILED")


class OrderItemModelTest(TestCase):
    """Test cases for OrderItem model."""

    def setUp(self):
        self.order = OrderFactory.create_order()
        self.product = ProductFactory.create_product(price=Decimal("50.00"))

    def test_create_order_item(self):
        """Test creating an order item."""
        item = OrderItemFactory.create_order_item(
            order=self.order, product=self.product, quantity=2
        )

        self.assertEqual(item.order, self.order)
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 2)

    def test_order_item_snapshots_product_details(self):
        """Test that order item snapshots product details."""
        item = OrderItemFactory.create_order_item(
            order=self.order, product=self.product
        )

        self.assertEqual(item.product_name, self.product.name)
        self.assertEqual(item.product_sku, self.product.sku)
        self.assertEqual(item.unit_price, self.product.price)

    def test_order_item_total_price(self):
        """Test order item total price calculation."""
        item = OrderItemFactory.create_order_item(
            order=self.order,
            product=self.product,
            quantity=3,
            unit_price=Decimal("50.00"),
        )

        self.assertEqual(item.total_price, Decimal("150.00"))

    def test_order_item_str_representation(self):
        """Test string representation of order item."""
        item = OrderItemFactory.create_order_item(
            order=self.order, product=self.product, quantity=2
        )

        str_repr = str(item)
        self.assertIn("2x", str_repr)

    def test_order_with_multiple_items(self):
        """Test order with multiple items."""
        OrderItemFactory.create_order_item(order=self.order, quantity=1)
        OrderItemFactory.create_order_item(order=self.order, quantity=2)
        OrderItemFactory.create_order_item(order=self.order, quantity=3)

        self.assertEqual(self.order.items.count(), 3)


class OrderRelationshipsTest(TestCase):
    """Test cases for order relationships."""

    def test_user_orders_relationship(self):
        """Test user-orders relationship."""
        user = UserFactory.create_customer()
        OrderFactory.create_order(user=user)
        OrderFactory.create_order(user=user)

        self.assertEqual(user.orders.count(), 2)

    def test_order_items_relationship(self):
        """Test order-items relationship."""
        order = OrderFactory.create_order_with_items(num_items=3)

        self.assertEqual(order.items.count(), 3)

    def test_shipping_address_relationship(self):
        """Test order-shipping_address relationship."""
        order = OrderFactory.create_order()

        self.assertIsNotNone(order.shipping_address)
        self.assertEqual(order.shipping_address.user, order.user)
