from rest_framework import serializers
from apps.cart.models import Cart, CartItem
from apps.products.serializers.product import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_id",
            "quantity",
            "total_price",
            "is_available",
        ]

    def validate(self, attrs):
        product_id = attrs.get("product_id")
        quantity = attrs.get("quantity", 1)

        from apps.products.models import Product
        from apps.products.constants import STATUS_PUBLISHED

        try:
            product = Product.objects.get(id=product_id)

            # Check if product is deleted or not published
            if product.is_deleted:
                raise serializers.ValidationError("This product is no longer available")

            if product.status != STATUS_PUBLISHED:
                raise serializers.ValidationError(
                    "This product is not available for purchase"
                )

            if hasattr(product, "inventory") and product.inventory.available < quantity:
                raise serializers.ValidationError(
                    f"Only {product.inventory.available} items available"
                )
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")

        return attrs


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()
    has_unavailable_items = serializers.ReadOnlyField()
    unavailable_items_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "items",
            "total_items",
            "subtotal",
            "has_unavailable_items",
            "unavailable_items_count",
            "created_at",
            "updated_at",
        ]

    def get_unavailable_items_count(self, obj) -> int:
        """Return count of unavailable items for frontend warning."""
        return obj.get_unavailable_items().count()
