from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.orders.serializers.order import OrderSerializer, CheckoutSerializer
from apps.orders.services.checkout_service import CheckoutService
from apps.orders.services.order_service import OrderService


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Order management viewset.

    Endpoints:
        GET  /api/orders/             - List user's orders
        GET  /api/orders/{id}/        - Get order details
        POST /api/orders/checkout/    - Create order from cart
        POST /api/orders/{id}/cancel/ - Cancel order
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return OrderService.get_user_orders(self.request.user)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        """Create order from cart"""
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = CheckoutService.create_order_from_cart(
                user=request.user,
                shipping_address_id=serializer.validated_data["shipping_address_id"],
                billing_address_id=serializer.validated_data.get("billing_address_id"),
                customer_notes=serializer.validated_data.get("customer_notes", ""),
            )
            order_serializer = OrderSerializer(order)
            return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()

        success, message = OrderService.cancel_order(order)

        if success:
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        else:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
