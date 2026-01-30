"""
Cart App API Tests

Comprehensive tests for Cart API endpoints.
"""

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.cart.models import Cart, CartItem
from apps.cart.tests.factories import (
    UserFactory,
    ProductFactory,
    CartFactory,
)


class CartAPITestCase(TestCase):
    """Base test case with authentication helpers."""

    def setUp(self):
        """Set up test client and data."""
        self.client = APIClient()
        self.customer = UserFactory.create_customer()
        self.shopkeeper = UserFactory.create_shopkeeper()
        self.product = ProductFactory.create_product(
            shopkeeper=self.shopkeeper, price=Decimal("100.00"), stock=10
        )

    def authenticate(self, user):
        """Authenticate the client with given user."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def get_cart_url(self):
        """Get cart list URL."""
        return reverse("cart-list")

    def get_add_item_url(self):
        """Get add item URL."""
        return reverse("cart-add-item")

    def get_update_item_url(self):
        """Get update item URL."""
        return reverse("cart-update-item")

    def get_remove_item_url(self):
        """Get remove item URL."""
        return reverse("cart-remove-item")

    def get_clear_url(self):
        """Get clear cart URL."""
        return reverse("cart-clear")


class CartListTest(CartAPITestCase):
    """Tests for cart list endpoint."""

    def test_get_cart_authenticated(self):
        """Test getting cart as authenticated customer."""
        self.authenticate(self.customer)
        cart = CartFactory.create_cart(user=self.customer)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        response = self.client.get(self.get_cart_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_items"], 2)
        self.assertEqual(len(response.data["items"]), 1)

    def test_get_cart_unauthenticated(self):
        """Test getting cart without authentication."""
        response = self.client.get(self.get_cart_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_cart_shopkeeper_forbidden(self):
        """Test that shopkeepers cannot access cart."""
        self.authenticate(self.shopkeeper)

        response = self.client.get(self.get_cart_url())

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_cart_creates_if_not_exists(self):
        """Test that getting cart creates one if not exists."""
        self.authenticate(self.customer)
        self.assertFalse(Cart.objects.filter(user=self.customer).exists())

        response = self.client.get(self.get_cart_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Cart.objects.filter(user=self.customer).exists())


class CartAddItemTest(CartAPITestCase):
    """Tests for add item endpoint."""

    def test_add_item_success(self):
        """Test adding item to cart."""
        self.authenticate(self.customer)

        response = self.client.post(
            self.get_add_item_url(),
            {"product_id": self.product.id, "quantity": 2},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_items"], 2)

    def test_add_item_default_quantity(self):
        """Test adding item with default quantity of 1."""
        self.authenticate(self.customer)

        response = self.client.post(
            self.get_add_item_url(),
            {"product_id": self.product.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_items"], 1)

    def test_add_item_increases_existing_quantity(self):
        """Test adding same product increases quantity."""
        self.authenticate(self.customer)
        cart = CartFactory.create_cart(user=self.customer)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        response = self.client.post(
            self.get_add_item_url(),
            {"product_id": self.product.id, "quantity": 3},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_items"], 5)

    def test_add_nonexistent_product(self):
        """Test adding non-existent product."""
        self.authenticate(self.customer)

        response = self.client.post(
            self.get_add_item_url(),
            {"product_id": 99999, "quantity": 1},
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_add_item_exceeding_stock(self):
        """Test adding quantity exceeding stock."""
        self.authenticate(self.customer)

        response = self.client.post(
            self.get_add_item_url(),
            {"product_id": self.product.id, "quantity": 15},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_add_item_unauthenticated(self):
        """Test adding item without authentication."""
        response = self.client.post(
            self.get_add_item_url(),
            {"product_id": self.product.id, "quantity": 1},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CartUpdateItemTest(CartAPITestCase):
    """Tests for update item endpoint."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.cart = CartFactory.create_cart(user=self.customer)
        self.cart_item = CartItem.objects.create(
            cart=self.cart, product=self.product, quantity=2
        )

    def test_update_item_success(self):
        """Test updating item quantity."""
        self.authenticate(self.customer)

        response = self.client.post(
            self.get_update_item_url(),
            {"item_id": self.cart_item.id, "quantity": 5},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.quantity, 5)

    def test_update_nonexistent_item(self):
        """Test updating non-existent item."""
        self.authenticate(self.customer)

        response = self.client.post(
            self.get_update_item_url(),
            {"item_id": 99999, "quantity": 5},
        )

        # View returns 400 for general exceptions caught
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND],
        )

    def test_update_item_exceeding_stock(self):
        """Test updating quantity exceeding stock."""
        self.authenticate(self.customer)

        response = self.client.post(
            self.get_update_item_url(),
            {"item_id": self.cart_item.id, "quantity": 15},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_other_user_item(self):
        """Test updating another user's item."""
        other_customer = UserFactory.create_customer()
        other_cart = CartFactory.create_cart(user=other_customer)
        other_item = CartItem.objects.create(
            cart=other_cart, product=self.product, quantity=1
        )

        self.authenticate(self.customer)

        response = self.client.post(
            self.get_update_item_url(),
            {"item_id": other_item.id, "quantity": 5},
        )

        # View returns 400 for items not belonging to user's cart
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND],
        )


class CartRemoveItemTest(CartAPITestCase):
    """Tests for remove item endpoint."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.cart = CartFactory.create_cart(user=self.customer)
        self.cart_item = CartItem.objects.create(
            cart=self.cart, product=self.product, quantity=2
        )

    def test_remove_item_success(self):
        """Test removing item from cart."""
        self.authenticate(self.customer)

        response = self.client.post(
            self.get_remove_item_url(),
            {"item_id": self.cart_item.id},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CartItem.objects.filter(id=self.cart_item.id).exists())

    def test_remove_nonexistent_item(self):
        """Test removing non-existent item."""
        self.authenticate(self.customer)

        response = self.client.post(
            self.get_remove_item_url(),
            {"item_id": 99999},
        )

        # View returns 400 for general exceptions caught
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND],
        )

    def test_remove_other_user_item(self):
        """Test removing another user's item."""
        other_customer = UserFactory.create_customer()
        other_cart = CartFactory.create_cart(user=other_customer)
        other_item = CartItem.objects.create(
            cart=other_cart, product=self.product, quantity=1
        )

        self.authenticate(self.customer)

        response = self.client.post(
            self.get_remove_item_url(),
            {"item_id": other_item.id},
        )

        # View returns 400 for items not belonging to user's cart
        self.assertIn(
            response.status_code,
            [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND],
        )


class CartClearTest(CartAPITestCase):
    """Tests for clear cart endpoint."""

    def test_clear_cart_success(self):
        """Test clearing all items from cart."""
        self.authenticate(self.customer)
        cart = CartFactory.create_cart(user=self.customer)
        product2 = ProductFactory.create_product(shopkeeper=self.shopkeeper)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        CartItem.objects.create(cart=cart, product=product2, quantity=3)

        response = self.client.post(self.get_clear_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_items"], 0)
        self.assertEqual(len(response.data["items"]), 0)

    def test_clear_empty_cart(self):
        """Test clearing already empty cart."""
        self.authenticate(self.customer)
        CartFactory.create_cart(user=self.customer)

        response = self.client.post(self.get_clear_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_clear_cart_unauthenticated(self):
        """Test clearing cart without authentication."""
        response = self.client.post(self.get_clear_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CartSubtotalTest(CartAPITestCase):
    """Tests for cart subtotal calculation."""

    def test_subtotal_calculation(self):
        """Test that subtotal is calculated correctly."""
        self.authenticate(self.customer)
        cart = CartFactory.create_cart(user=self.customer)
        product2 = ProductFactory.create_product(
            shopkeeper=self.shopkeeper, price=Decimal("50.00")
        )

        CartItem.objects.create(cart=cart, product=self.product, quantity=2)  # 200
        CartItem.objects.create(cart=cart, product=product2, quantity=3)  # 150

        response = self.client.get(self.get_cart_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data["subtotal"]), Decimal("350.00"))
