"""
Product Filters

Custom filters for product listing with slug-based filtering.
"""

from django_filters import rest_framework as filters
from apps.products.models import Product


class ProductFilter(filters.FilterSet):
    """
    Custom filter for products.

    Supports filtering by:
    - category: Category slug (e.g., ?category=electronics)
    - brand: Brand slug (e.g., ?brand=apple)
    - is_featured: Boolean (e.g., ?is_featured=true)
    - min_price: Minimum price (e.g., ?min_price=100)
    - max_price: Maximum price (e.g., ?max_price=1000)
    """

    category = filters.CharFilter(
        field_name="category__slug",
        lookup_expr="iexact",
        help_text="Filter by category slug",
    )
    brand = filters.CharFilter(
        field_name="brand__slug",
        lookup_expr="iexact",
        help_text="Filter by brand slug",
    )
    is_featured = filters.BooleanFilter(
        field_name="is_featured",
        help_text="Filter featured products",
    )
    min_price = filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
        help_text="Minimum price",
    )
    max_price = filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
        help_text="Maximum price",
    )

    class Meta:
        model = Product
        fields = ["category", "brand", "is_featured", "min_price", "max_price"]
