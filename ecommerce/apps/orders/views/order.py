from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.orders.serializers.order import OrderSerializer, CheckoutSerializer
from apps.orders.serializers.return_serializer import (
    ReturnRequestSerializer,
    ReturnRequestCreateSerializer,
)
from apps.orders.services.checkout_service import CheckoutService
from apps.orders.services.order_service import OrderService
from apps.accounts.permissions import IsCustomer


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Order management viewset.

    Endpoints:
        GET  /api/v1/orders/             - List user's orders
        GET  /api/v1/orders/{id}/        - Get order details
        POST /api/v1/orders/checkout/    - Create order from cart
        POST /api/v1/orders/{id}/cancel/ - Cancel order
        POST /api/v1/orders/{id}/return/ - Request return for delivered order
        GET  /api/v1/orders/{id}/return-status/ - Check return request status

    Permissions:
        - Only authenticated customers can access orders
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomer]

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

    @action(detail=True, methods=["post"], url_path="return")
    def request_return(self, request, pk=None):
        """
        Request return for a delivered order.

        POST /api/orders/{id}/return/
        Body: {
            "reason": "DEFECTIVE",
            "description": "Item arrived broken"
        }

        Returns:
            - 201: Return request created
            - 400: Order not eligible for return
        """
        order = self.get_object()

        # Validate input
        serializer = ReturnRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create return request
        return_request, message = OrderService.request_return(
            order=order,
            reason=serializer.validated_data["reason"],
            description=serializer.validated_data.get("description", ""),
        )

        if return_request:
            response_serializer = ReturnRequestSerializer(return_request)
            return Response(
                {
                    "message": message,
                    "return_request": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="return-status")
    def return_status(self, request, pk=None):
        """
        Check return request status for an order.

        GET /api/orders/{id}/return-status/

        Returns:
            - 200: Return request details
            - 404: No return request found
        """
        order = self.get_object()

        return_request = OrderService.get_return_request(order)

        if return_request:
            serializer = ReturnRequestSerializer(return_request)
            return Response(serializer.data)
        else:
            return Response(
                {"error": "No return request found for this order"},
                status=status.HTTP_404_NOT_FOUND,
            )
