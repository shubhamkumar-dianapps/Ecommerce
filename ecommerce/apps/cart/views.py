from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.cart.models import Cart, CartItem
from apps.products.models import Product
from apps.cart.serializers import CartSerializer
from apps.cart.services import CartService
from apps.accounts.permissions import IsCustomer


class CartViewSet(viewsets.ViewSet):
    """
    Cart management viewset.

    Endpoints:
        GET  /api/v1/cart/             - Get user's cart
        POST /api/v1/cart/add_item/    - Add item to cart
        POST /api/v1/cart/update_item/ - Update item quantity
        POST /api/v1/cart/remove_item/ - Remove item from cart
        POST /api/v1/cart/clear/       - Clear all items

    Permissions:
        - Only authenticated customers can access cart
    """

    permission_classes = [permissions.IsAuthenticated, IsCustomer]

    def list(self, request):
        """Get user's cart."""
        cart = CartService.get_or_create_cart(request.user)
        serializer = CartSerializer(cart, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        """Add an item to the cart."""
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        # Validate product_id
        if product_id is None:
            return Response(
                {"error": "product_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate quantity
        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError("quantity must be at least 1")
        except (TypeError, ValueError):
            return Response(
                {"error": "quantity must be a positive integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cart, created = CartService.add_item(request.user, product_id, quantity)
            serializer = CartSerializer(cart, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def update_item(self, request):
        """Update the quantity of a cart item."""
        item_id = request.data.get("item_id")
        quantity = request.data.get("quantity")

        # Validate item_id
        if item_id is None:
            return Response(
                {"error": "item_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate quantity
        if quantity is None:
            return Response(
                {"error": "quantity is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            item_id = int(item_id)
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError("quantity must be non-negative")
        except (TypeError, ValueError):
            return Response(
                {"error": "item_id and quantity must be valid integers"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cart = CartService.update_item(request.user, item_id, quantity)
            serializer = CartSerializer(cart, context={"request": request})
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def remove_item(self, request):
        """Remove an item from the cart."""
        item_id = request.data.get("item_id")

        # Validate item_id
        if item_id is None:
            return Response(
                {"error": "item_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            item_id = int(item_id)
        except (TypeError, ValueError):
            return Response(
                {"error": "item_id must be a valid integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cart = CartService.remove_item(request.user, item_id)
            serializer = CartSerializer(cart, context={"request": request})
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["post"])
    def clear(self, request):
        """Clear all items from the cart."""
        try:
            cart = CartService.clear_cart(request.user)
            serializer = CartSerializer(cart, context={"request": request})
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND
            )
