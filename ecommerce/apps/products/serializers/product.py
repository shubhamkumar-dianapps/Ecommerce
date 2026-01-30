from rest_framework import serializers
from apps.products.models import Category, Brand, Product, ProductImage, Inventory


class CategorySerializer(serializers.ModelSerializer):
    # Uses annotation from queryset - no extra DB query per category!
    children_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


class InventorySerializer(serializers.ModelSerializer):
    available = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Inventory
        fields = "__all__"
        read_only_fields = ("reserved",)


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    primary_image = serializers.SerializerMethodField()
    is_on_sale = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "price",
            "compare_at_price",
            "category_name",
            "brand_name",
            "primary_image",
            "is_on_sale",
            "discount_percentage",
            "is_featured",
            "status",
        ]

    def get_primary_image(self, obj):
        # Uses prefetched 'primary_images' from queryset - no extra DB query!
        primary_images = getattr(obj, "primary_images", None)
        if primary_images:
            primary = primary_images[0] if primary_images else None
            if primary and primary.image:
                return self.context["request"].build_absolute_uri(primary.image.url)
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    inventory = InventorySerializer(read_only=True)
    is_on_sale = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = "__all__"
