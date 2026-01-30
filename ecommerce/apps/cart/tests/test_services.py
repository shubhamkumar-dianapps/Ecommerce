"""
Cart App Service Tests

Comprehensive tests for CartService business logic.
"""

from decimal import Decimal
from django.test import TestCase
from apps.cart.models import Cart, CartItem
from apps.cart.services import CartService
from apps.products.models import Product
from apps.cart.tests.factories import (
    UserFactory,
    ProductFactory,
    CartFactory,
)


class CartServiceGetOrCreateTest(TestCase):
    """Tests for CartService.get_or_create_cart method."""

    def setUp(self):
        """Set up test data."""
        self.customer = UserFactory.create_customer()

    def test_create_cart_for_new_user(self):
        """Test creating a cart for user without one."""
        self.assertFalse(Cart.objects.filter(user=self.customer).exists())

        cart = CartService.get_or_create_cart(self.customer)

        self.assertIsNotNone(cart)
        self.assertEqual(cart.user, self.customer)
        self.assertTrue(Cart.objects.filter(user=self.customer).exists())

    def test_get_existing_cart(self):
        """Test getting existing cart."""
        existing_cart = Cart.objects.create(user=self.customer)

        cart = CartService.get_or_create_cart(self.customer)

        self.assertEqual(cart.id, existing_cart.id)
        self.assertEqual(Cart.objects.filter(user=self.customer).count(), 1)


class CartServiceAddItemTest(TestCase):
    """Tests for CartService.add_item method."""

    def setUp(self):
        """Set up test data."""
        self.customer = UserFactory.create_customer()
        self.shopkeeper = UserFactory.create_shopkeeper()
        self.product = ProductFactory.create_product(
            shopkeeper=self.shopkeeper, price=Decimal("100.00"), stock=10
        )

    def test_add_new_item_to_cart(self):
        """Test adding a new item to cart."""
        cart, created = CartService.add_item(self.customer, self.product.id, 2)

        self.assertTrue(created)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 2)
        self.assertEqual(cart.items.first().product, self.product)

    def test_add_item_creates_cart_if_not_exists(self):
        """Test that adding item creates cart if needed."""
        self.assertFalse(Cart.objects.filter(user=self.customer).exists())

        cart, _ = CartService.add_item(self.customer, self.product.id, 1)

        self.assertTrue(Cart.objects.filter(user=self.customer).exists())

    def test_add_existing_item_increases_quantity(self):
        """Test adding same product increases quantity."""
        CartService.add_item(self.customer, self.product.id, 2)
        cart, created = CartService.add_item(self.customer, self.product.id, 3)

        self.assertFalse(created)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 5)

    def test_add_item_default_quantity(self):
        """Test default quantity is 1."""
        cart, _ = CartService.add_item(self.customer, self.product.id)

        self.assertEqual(cart.items.first().quantity, 1)

    def test_add_nonexistent_product_raises_error(self):
        """Test adding non-existent product raises error."""
        with self.assertRaises(Product.DoesNotExist):
            CartService.add_item(self.customer, 99999, 1)

    def test_add_item_exceeding_stock_raises_error(self):
        """Test adding quantity exceeding stock raises error."""
        with self.assertRaises(ValueError):
            CartService.add_item(self.customer, self.product.id, 15)


class CartServiceUpdateItemTest(TestCase):
    """Tests for CartService.update_item method."""

    def setUp(self):
        """Set up test data."""
        self.customer = UserFactory.create_customer()
        self.shopkeeper = UserFactory.create_shopkeeper()
        self.product = ProductFactory.create_product(
            shopkeeper=self.shopkeeper, stock=10
        )
        self.cart = CartFactory.create_cart(user=self.customer)
        self.cart_item = CartItem.objects.create(
            cart=self.cart, product=self.product, quantity=2
        )

    def test_update_item_quantity(self):
        """Test updating item quantity."""
        CartService.update_item(self.customer, self.cart_item.id, 5)

        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.quantity, 5)

    def test_update_nonexistent_item_raises_error(self):
        """Test updating non-existent item raises error."""
        with self.assertRaises(CartItem.DoesNotExist):
            CartService.update_item(self.customer, 99999, 5)

    def test_update_other_user_item_raises_error(self):
        """Test updating another user's item raises error."""
        other_customer = UserFactory.create_customer()
        other_cart = CartFactory.create_cart(user=other_customer)
        other_item = CartItem.objects.create(
            cart=other_cart, product=self.product, quantity=1
        )

        with self.assertRaises(CartItem.DoesNotExist):
            CartService.update_item(self.customer, other_item.id, 5)

    def test_update_quantity_exceeding_stock_raises_error(self):
        """Test updating quantity beyond stock raises error."""
        with self.assertRaises(ValueError):
            CartService.update_item(self.customer, self.cart_item.id, 15)


class CartServiceRemoveItemTest(TestCase):
    """Tests for CartService.remove_item method."""

    def setUp(self):
        """Set up test data."""
        self.customer = UserFactory.create_customer()
        self.product = ProductFactory.create_product()
        self.cart = CartFactory.create_cart(user=self.customer)
        self.cart_item = CartItem.objects.create(
            cart=self.cart, product=self.product, quantity=2
        )

    def test_remove_item_from_cart(self):
        """Test removing item from cart."""
        cart = CartService.remove_item(self.customer, self.cart_item.id)

        self.assertEqual(cart.items.count(), 0)
        self.assertFalse(CartItem.objects.filter(id=self.cart_item.id).exists())

    def test_remove_nonexistent_item_raises_error(self):
        """Test removing non-existent item raises error."""
        with self.assertRaises(CartItem.DoesNotExist):
            CartService.remove_item(self.customer, 99999)

    def test_remove_other_user_item_raises_error(self):
        """Test removing another user's item raises error."""
        other_customer = UserFactory.create_customer()
        other_cart = CartFactory.create_cart(user=other_customer)
        other_item = CartItem.objects.create(
            cart=other_cart, product=self.product, quantity=1
        )

        with self.assertRaises(CartItem.DoesNotExist):
            CartService.remove_item(self.customer, other_item.id)


class CartServiceClearCartTest(TestCase):
    """Tests for CartService.clear_cart method."""

    def setUp(self):
        """Set up test data."""
        self.customer = UserFactory.create_customer()
        self.product1 = ProductFactory.create_product()
        self.product2 = ProductFactory.create_product()
        self.cart = CartFactory.create_cart(user=self.customer)

    def test_clear_cart_removes_all_items(self):
        """Test clearing cart removes all items."""
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2)
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=3)

        self.assertEqual(self.cart.items.count(), 2)

        cart = CartService.clear_cart(self.customer)

        self.assertEqual(cart.items.count(), 0)

    def test_clear_empty_cart(self):
        """Test clearing already empty cart."""
        cleared_cart = CartService.clear_cart(self.customer)

        self.assertEqual(cleared_cart.items.count(), 0)

    def test_clear_cart_preserves_cart(self):
        """Test that clearing cart doesn't delete the cart itself."""
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=1)

        CartService.clear_cart(self.customer)

        self.assertTrue(Cart.objects.filter(user=self.customer).exists())

    def test_clear_nonexistent_cart_raises_error(self):
        """Test clearing non-existent cart raises error."""
        other_customer = UserFactory.create_customer()

        with self.assertRaises(Cart.DoesNotExist):
            CartService.clear_cart(other_customer)
