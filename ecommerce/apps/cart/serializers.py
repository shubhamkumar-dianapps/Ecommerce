from rest_framework import serializers
from apps.cart.models import Cart, CartItem
from apps.products.serializers.product import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "total_price"]

    def validate(self, attrs):
        product_id = attrs.get("product_id")
        quantity = attrs.get("quantity", 1)

        from apps.products.models import Product

        try:
            product = Product.objects.get(id=product_id)
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

    class Meta:
        model = Cart
        fields = ["id", "items", "total_items", "subtotal", "created_at", "updated_at"]
