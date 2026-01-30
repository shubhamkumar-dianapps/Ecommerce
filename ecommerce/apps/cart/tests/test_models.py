"""
Cart App Model Tests

Comprehensive tests for Cart and CartItem models.
"""

from decimal import Decimal
from django.test import TestCase
from django.db import IntegrityError
from apps.cart.models import Cart, CartItem
from apps.cart.tests.factories import (
    UserFactory,
    ProductFactory,
    CartFactory,
)


class CartModelTest(TestCase):
    """Tests for Cart model."""

    def setUp(self):
        """Set up test data."""
        self.customer = UserFactory.create_customer()
        self.shopkeeper = UserFactory.create_shopkeeper()
        self.product1 = ProductFactory.create_product(
            shopkeeper=self.shopkeeper, price=Decimal("100.00")
        )
        self.product2 = ProductFactory.create_product(
            shopkeeper=self.shopkeeper, price=Decimal("50.00")
        )

    def test_create_cart_success(self):
        """Test creating a cart for a user."""
        cart = Cart.objects.create(user=self.customer)

        self.assertEqual(cart.user, self.customer)
        self.assertIsNotNone(cart.created_at)
        self.assertIsNotNone(cart.updated_at)

    def test_one_cart_per_user(self):
        """Test that each user can only have one cart."""
        Cart.objects.create(user=self.customer)

        with self.assertRaises(IntegrityError):
            Cart.objects.create(user=self.customer)

    def test_total_items_empty_cart(self):
        """Test total_items property for empty cart."""
        cart = CartFactory.create_cart(user=self.customer)

        self.assertEqual(cart.total_items, 0)

    def test_total_items_with_items(self):
        """Test total_items property with multiple items."""
        cart = CartFactory.create_cart(user=self.customer)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=2)
        CartItem.objects.create(cart=cart, product=self.product2, quantity=3)

        self.assertEqual(cart.total_items, 5)

    def test_subtotal_empty_cart(self):
        """Test subtotal property for empty cart."""
        cart = CartFactory.create_cart(user=self.customer)

        self.assertEqual(cart.subtotal, 0)

    def test_subtotal_with_items(self):
        """Test subtotal calculation with multiple items."""
        cart = CartFactory.create_cart(user=self.customer)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=2)  # 200
        CartItem.objects.create(cart=cart, product=self.product2, quantity=3)  # 150

        self.assertEqual(cart.subtotal, Decimal("350.00"))

    def test_clear_cart(self):
        """Test clear method removes all items."""
        cart = CartFactory.create_cart(user=self.customer)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=2)
        CartItem.objects.create(cart=cart, product=self.product2, quantity=3)

        self.assertEqual(cart.items.count(), 2)

        cart.clear()

        self.assertEqual(cart.items.count(), 0)
        # Cart still exists
        self.assertTrue(Cart.objects.filter(id=cart.id).exists())

    def test_str_representation(self):
        """Test __str__ method."""
        cart = CartFactory.create_cart(user=self.customer)

        self.assertEqual(str(cart), f"Cart for {self.customer.email}")


class CartItemModelTest(TestCase):
    """Tests for CartItem model."""

    def setUp(self):
        """Set up test data."""
        self.customer = UserFactory.create_customer()
        self.shopkeeper = UserFactory.create_shopkeeper()
        self.product = ProductFactory.create_product(
            shopkeeper=self.shopkeeper, price=Decimal("100.00"), stock=10
        )
        self.cart = CartFactory.create_cart(user=self.customer)

    def test_create_cart_item_success(self):
        """Test creating a cart item."""
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
        )

        self.assertEqual(item.cart, self.cart)
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 2)

    def test_unique_constraint_cart_product(self):
        """Test that same product can only be added once per cart."""
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1,
        )

        with self.assertRaises(IntegrityError):
            CartItem.objects.create(
                cart=self.cart,
                product=self.product,
                quantity=2,
            )

    def test_total_price_property(self):
        """Test total_price calculation."""
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3,
        )

        self.assertEqual(item.total_price, Decimal("300.00"))

    def test_stock_validation_on_save(self):
        """Test that quantity exceeding stock raises error."""
        with self.assertRaises(ValueError) as context:
            CartItem.objects.create(
                cart=self.cart,
                product=self.product,
                quantity=15,  # Exceeds stock of 10
            )

        self.assertIn("Insufficient stock", str(context.exception))

    def test_update_quantity_stock_validation(self):
        """Test stock validation when updating quantity."""
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=5,
        )

        item.quantity = 15  # Exceeds stock

        with self.assertRaises(ValueError):
            item.save()

    def test_str_representation(self):
        """Test __str__ method."""
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
        )

        self.assertEqual(str(item), f"2 x {self.product.name}")

    def test_default_quantity(self):
        """Test default quantity is 1."""
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
        )

        self.assertEqual(item.quantity, 1)
