from django.db import transaction
from apps.orders.models import Order, OrderItem
from apps.cart.models import Cart
from apps.addresses.models import Address


class CheckoutService:
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(
        user, shipping_address_id, billing_address_id=None, customer_notes=""
    ):
        """
        Create an order from user's cart and reserve inventory
        """
        # Get cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise ValueError("Cart is empty")

        if not cart.items.exists():
            raise ValueError("Cart is empty")

        # Get addresses
        shipping_address = Address.objects.get(id=shipping_address_id, user=user)
        billing_address = shipping_address
        if billing_address_id:
            billing_address = Address.objects.get(id=billing_address_id, user=user)

        # Calculate totals
        subtotal = cart.subtotal
        shipping_cost = CheckoutService._calculate_shipping(cart)
        tax = CheckoutService._calculate_tax(subtotal)
        total = subtotal + shipping_cost + tax

        # Create order
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax=tax,
            total=total,
            customer_notes=customer_notes,
        )

        # Create order items and reserve inventory
        for cart_item in cart.items.all():
            # Reserve inventory
            if hasattr(cart_item.product, "inventory"):
                success = cart_item.product.inventory.reserve(cart_item.quantity)
                if not success:
                    raise ValueError(f"Insufficient stock for {cart_item.product.name}")

            # Create order item
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
            )

        # Clear cart
        cart.clear()

        return order

    @staticmethod
    def _calculate_shipping(cart):
        """Calculate shipping cost (placeholder)"""
        # Simple logic: free shipping over $100
        if cart.subtotal > 100:
            return 0
        return 10

    @staticmethod
    def _calculate_tax(subtotal):
        """Calculate tax (placeholder)"""
        # Simple 10% tax
        return subtotal * 0.10
