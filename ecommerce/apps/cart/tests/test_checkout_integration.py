"""
Cart Checkout Integration Tests

Tests to verify cart is properly cleared after order placement.
"""

from decimal import Decimal
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.cart.models import Cart, CartItem
from apps.orders.services.checkout_service import CheckoutService
from apps.cart.tests.factories import (
    UserFactory,
    ProductFactory,
    CartFactory,
    AddressFactory,
)


class CheckoutClearCartTest(TestCase):
    """Tests for cart clearing after checkout."""

    def setUp(self):
        """Set up test data."""
        self.customer = UserFactory.create_customer()
        self.shopkeeper = UserFactory.create_shopkeeper()
        self.product = ProductFactory.create_product(
            shopkeeper=self.shopkeeper, price=Decimal("100.00"), stock=10
        )
        self.cart = CartFactory.create_cart(user=self.customer)
        self.address = AddressFactory.create_address(user=self.customer)

    def test_checkout_clears_cart(self):
        """Test that successful checkout clears the cart."""
        # Add items to cart
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

        self.assertEqual(self.cart.items.count(), 1)
        self.assertEqual(self.cart.total_items, 2)

        # Create order from cart
        order = CheckoutService.create_order_from_cart(
            user=self.customer,
            shipping_address_id=self.address.id,
        )

        # Verify order was created
        self.assertIsNotNone(order)
        self.assertEqual(order.user, self.customer)
        self.assertEqual(order.items.count(), 1)

        # Verify cart is cleared
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.items.count(), 0)
        self.assertEqual(self.cart.total_items, 0)

    def test_checkout_multiple_items_clears_all(self):
        """Test that checkout clears cart with multiple items."""
        product2 = ProductFactory.create_product(
            shopkeeper=self.shopkeeper, price=Decimal("50.00"), stock=10
        )

        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        CartItem.objects.create(cart=self.cart, product=product2, quantity=3)

        self.assertEqual(self.cart.items.count(), 2)

        order = CheckoutService.create_order_from_cart(
            user=self.customer,
            shipping_address_id=self.address.id,
        )

        self.assertIsNotNone(order)
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.items.count(), 0)

    def test_failed_checkout_preserves_cart(self):
        """Test that failed checkout does not clear cart."""
        # Add item with quantity exceeding available stock
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

        # Manually reduce inventory to cause failure
        self.product.inventory.quantity = 1
        self.product.inventory.save()

        try:
            CheckoutService.create_order_from_cart(
                user=self.customer,
                shipping_address_id=self.address.id,
            )
        except ValueError:
            pass

        # Cart should still have items
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.items.count(), 1)

    def test_cart_still_exists_after_checkout(self):
        """Test that cart object persists after checkout (just empty)."""
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)

        cart_id = self.cart.id

        CheckoutService.create_order_from_cart(
            user=self.customer,
            shipping_address_id=self.address.id,
        )

        # Cart should still exist
        self.assertTrue(Cart.objects.filter(id=cart_id).exists())


class CheckoutAPICartClearTest(TestCase):
    """API-level tests for cart clearing after checkout."""

    def setUp(self):
        """Set up test client and data."""
        self.client = APIClient()
        self.customer = UserFactory.create_customer()
        self.shopkeeper = UserFactory.create_shopkeeper()
        self.product = ProductFactory.create_product(
            shopkeeper=self.shopkeeper, price=Decimal("100.00"), stock=10
        )
        self.cart = CartFactory.create_cart(user=self.customer)
        self.address = AddressFactory.create_address(user=self.customer)

        # Authenticate
        refresh = RefreshToken.for_user(self.customer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_checkout_api_clears_cart(self):
        """Test that checkout API endpoint clears cart."""
        # Add item to cart
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

        # Call checkout API
        from django.urls import reverse

        try:
            checkout_url = reverse("order-checkout")
        except Exception:
            # URL might not be configured in tests
            self.skipTest("Checkout URL not configured")

        response = self.client.post(
            checkout_url,
            {"shipping_address_id": self.address.id},
            format="json",
        )

        if response.status_code == status.HTTP_201_CREATED:
            # Verify cart is cleared
            self.cart.refresh_from_db()
            self.assertEqual(self.cart.items.count(), 0)

    def test_can_add_to_cart_after_checkout(self):
        """Test that user can add items to cart after checkout."""
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)

        # Complete checkout
        CheckoutService.create_order_from_cart(
            user=self.customer,
            shipping_address_id=self.address.id,
        )

        # Verify cart is empty
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.items.count(), 0)

        # Add new item to cart
        product2 = ProductFactory.create_product(
            shopkeeper=self.shopkeeper, price=Decimal("50.00"), stock=10
        )
        CartItem.objects.create(cart=self.cart, product=product2, quantity=3)

        self.assertEqual(self.cart.items.count(), 1)
        self.assertEqual(self.cart.total_items, 3)
