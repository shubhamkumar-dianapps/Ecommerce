"""
Cart Service

Business logic for shopping cart operations.
"""

from typing import Tuple
from django.db import transaction
from apps.cart.models import Cart, CartItem
from apps.products.models import Product


class CartService:
    """Service class for cart operations."""

    @staticmethod
    def get_or_create_cart(user) -> Cart:
        """
        Get or create a cart for the user.

        Args:
            user: User instance

        Returns:
            Cart instance
        """
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    @transaction.atomic
    def add_item(user, product_id: int, quantity: int = 1) -> Tuple[Cart, bool]:
        """
        Add an item to the user's cart.

        Args:
            user: User instance
            product_id: Product ID to add
            quantity: Quantity to add (default: 1)

        Returns:
            Tuple of (Cart, created) where created indicates if new item was added

        Raises:
            Product.DoesNotExist: If product not found
            ValueError: If insufficient stock
        """
        cart = CartService.get_or_create_cart(user)
        product = Product.objects.get(id=product_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart, created

    @staticmethod
    @transaction.atomic
    def update_item(user, item_id: int, quantity: int) -> Cart:
        """
        Update the quantity of a cart item.

        Args:
            user: User instance
            item_id: Cart item ID
            quantity: New quantity

        Returns:
            Updated Cart instance

        Raises:
            CartItem.DoesNotExist: If cart item not found
            ValueError: If quantity exceeds available stock
        """
        cart = Cart.objects.get(user=user)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        cart_item.quantity = quantity
        cart_item.save()
        return cart

    @staticmethod
    @transaction.atomic
    def remove_item(user, item_id: int) -> Cart:
        """
        Remove an item from the cart.

        Args:
            user: User instance
            item_id: Cart item ID to remove

        Returns:
            Updated Cart instance

        Raises:
            CartItem.DoesNotExist: If cart item not found
        """
        cart = Cart.objects.get(user=user)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        cart_item.delete()
        return cart

    @staticmethod
    def clear_cart(user) -> Cart:
        """
        Clear all items from the user's cart.

        Args:
            user: User instance

        Returns:
            Empty Cart instance
        """
        cart = Cart.objects.get(user=user)
        cart.clear()
        return cart
