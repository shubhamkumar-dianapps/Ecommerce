"""
Tests for Order API Endpoints

Comprehensive tests for order listing, checkout, cancellation, and returns.
"""

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.orders.tests.factories import OrderFactory
from apps.accounts.tests.factories import UserFactory
from apps.addresses.tests.factories import AddressFactory
from apps.products.tests.factories import ProductFactory
from apps.cart.models import Cart, CartItem


class OrderListAPITest(TestCase):
    """Test cases for order list endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory.create_customer()
        self.url = reverse("order-list")

    def test_list_orders_authenticated(self):
        """Test listing orders when authenticated."""
        OrderFactory.create_order(user=self.user)
        OrderFactory.create_order(user=self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_orders_unauthenticated(self):
        """Test listing orders without authentication fails."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_only_own_orders(self):
        """Test that users only see their own orders."""
        other_user = UserFactory.create_customer()
        OrderFactory.create_order(user=self.user)
        OrderFactory.create_order(user=other_user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(len(response.data), 1)


class OrderDetailAPITest(TestCase):
    """Test cases for order detail endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory.create_customer()
        self.order = OrderFactory.create_order_with_items(user=self.user)
        self.url = reverse("order-detail", kwargs={"pk": self.order.pk})

    def test_retrieve_order(self):
        """Test retrieving order detail."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_number"], self.order.order_number)

    def test_retrieve_other_user_order_fails(self):
        """Test retrieving another user's order fails."""
        other_user = UserFactory.create_customer()
        self.client.force_authenticate(user=other_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CheckoutAPITest(TestCase):
    """Test cases for checkout endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory.create_customer()
        self.url = reverse("order-checkout")
        self.address = AddressFactory.create_address(user=self.user, is_default=True)
        self.product = ProductFactory.create_product(price=Decimal("100.00"))

        # Setup cart with items
        self.cart, _ = Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_checkout_success(self):
        """Test successful checkout."""
        self.client.force_authenticate(user=self.user)

        data = {"shipping_address_id": self.address.id}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("order", response.data)

    def test_checkout_empty_cart(self):
        """Test checkout with empty cart fails."""
        CartItem.objects.filter(cart=self.cart).delete()

        self.client.force_authenticate(user=self.user)

        data = {"shipping_address_id": self.address.id}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_unauthenticated(self):
        """Test checkout without authentication fails."""
        data = {"shipping_address_id": self.address.id}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_checkout_invalid_address(self):
        """Test checkout with invalid address fails."""
        self.client.force_authenticate(user=self.user)

        data = {"shipping_address_id": 99999}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_checkout_other_user_address(self):
        """Test checkout with another user's address fails."""
        other_user = UserFactory.create_customer()
        other_address = AddressFactory.create_address(user=other_user)

        self.client.force_authenticate(user=self.user)

        data = {"shipping_address_id": other_address.id}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CancelOrderAPITest(TestCase):
    """Test cases for order cancellation endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory.create_customer()
        self.order = OrderFactory.create_order(user=self.user, status="PENDING")
        self.url = reverse("order-cancel", kwargs={"pk": self.order.pk})

    def test_cancel_pending_order(self):
        """Test cancelling a pending order."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "CANCELLED")

    def test_cancel_shipped_order_fails(self):
        """Test cancelling a shipped order fails."""
        self.order.status = "SHIPPED"
        self.order.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_other_user_order_fails(self):
        """Test cancelling another user's order fails."""
        other_user = UserFactory.create_customer()
        self.client.force_authenticate(user=other_user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ReturnOrderAPITest(TestCase):
    """Test cases for order return endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory.create_customer()
        self.order = OrderFactory.create_order(user=self.user, status="DELIVERED")
        self.url = reverse("order-request-return", kwargs={"pk": self.order.pk})

    def test_request_return_delivered_order(self):
        """Test requesting return for delivered order."""
        self.client.force_authenticate(user=self.user)

        data = {"reason": "Product defective"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_request_return_pending_order_fails(self):
        """Test requesting return for pending order fails."""
        self.order.status = "PENDING"
        self.order.save()

        self.client.force_authenticate(user=self.user)

        data = {"reason": "Changed mind"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_return_without_reason_fails(self):
        """Test requesting return without reason fails."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
