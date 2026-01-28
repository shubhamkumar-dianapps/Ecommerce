from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.orders.models import Order
from apps.orders.serializers.order import OrderSerializer, CheckoutSerializer
from apps.orders.services.checkout_service import CheckoutService


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")

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
        if order.status in [Order.OrderStatus.DELIVERED, Order.OrderStatus.CANCELLED]:
            return Response(
                {"error": "Cannot cancel this order"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = Order.OrderStatus.CANCELLED

        # Release reserved inventory
        for item in order.items.all():
            if hasattr(item.product, "inventory"):
                item.product.inventory.release(item.quantity)

        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)
