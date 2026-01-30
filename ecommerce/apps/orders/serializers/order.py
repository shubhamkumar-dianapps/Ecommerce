from rest_framework import serializers
from apps.orders.models import Order, OrderItem
from apps.addresses.serializers import AddressSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_name",
            "product_sku",
            "unit_price",
            "quantity",
            "total_price",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "items",
            "shipping_address",
            "billing_address",
            "subtotal",
            "shipping_cost",
            "tax",
            "total",
            "status",
            "payment_status",
            "customer_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["order_number", "created_at", "updated_at"]


class CheckoutSerializer(serializers.Serializer):
    shipping_address_id = serializers.IntegerField()
    billing_address_id = serializers.IntegerField(required=False, allow_null=True)
    customer_notes = serializers.CharField(required=False, allow_blank=True)
