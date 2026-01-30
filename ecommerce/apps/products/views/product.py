"""
Product Views

Production-ready views with proper permissions, pagination, and filtering.
"""

from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.products.models import Category, Brand, Product
from apps.products.serializers.product import (
    CategorySerializer,
    BrandSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
)
from apps.products.permissions import IsShopkeeperOrReadOnly, IsProductOwner
from apps.products.pagination import (
    ProductPagination,
    CategoryPagination,
    BrandPagination,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Category ViewSet

    Endpoints:
    - GET /api/categories/ - List active categories
    - GET /api/categories/{slug}/ - Get category details

    Features:
    - Public access (no authentication required)
    - Pagination (20 per page)
    - Only active categories shown
    """

    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"
    pagination_class = CategoryPagination

    def get_queryset(self):
        """
        Get categories with annotated children_count.
        This prevents N+1 queries when serializing.
        """
        from django.db.models import Count

        return Category.objects.filter(is_active=True).annotate(
            children_count=Count("children")
        )


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Brand ViewSet

    Endpoints:
    - GET /api/brands/ - List active brands
    - GET /api/brands/{slug}/ - Get brand details

    Features:
    - Public access (no authentication required)
    - Pagination (20 per page)
    - Only active brands shown
    """

    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"
    pagination_class = BrandPagination


class ProductViewSet(viewsets.ModelViewSet):
    """
    Product ViewSet

    Endpoints:
    - GET /api/products/ - List published products (public)
    - GET /api/products/{slug}/ - Get product details (public)
    - GET /api/products/my-products/ - Get shopkeeper's own products (all statuses)
    - POST /api/products/ - Create product (verified shopkeepers only)
    - PUT/PATCH /api/products/{slug}/ - Update product (owner only)
    - DELETE /api/products/{slug}/ - Delete product (owner only)

    Features:
    - Public: View published products only
    - Shopkeepers: View all own products (draft, published, etc.)
    - Pagination (10 per page)
    - Filtering by category, brand, is_featured
    - Search by name, description, SKU
    - Ordering by price, created_at, name

    Permissions:
    - Read: Anyone (published products)
    - Create: Verified shopkeepers only
    - Update/Delete: Product owner only
    """

    permission_classes = [IsShopkeeperOrReadOnly, IsProductOwner]
    lookup_field = "slug"
    pagination_class = ProductPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "brand", "is_featured"]
    search_fields = ["name", "description", "sku"]
    ordering_fields = ["price", "created_at", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Get queryset based on user type.

        - Public/Customers: Only published products
        - Shopkeepers (my-products action): All own products

        Optimized with Prefetch to avoid N+1 queries.
        """
        from django.db.models import Prefetch
        from apps.products.models import ProductImage

        # Prefetch only primary images to avoid N+1
        primary_image_prefetch = Prefetch(
            "images",
            queryset=ProductImage.objects.filter(is_primary=True),
            to_attr="primary_images",
        )

        # For my-products action, show all shopkeeper's products
        if self.action == "my_products":
            if self.request.user.is_authenticated:
                return (
                    Product.objects.filter(shopkeeper=self.request.user)
                    .select_related("category", "brand")
                    .prefetch_related(primary_image_prefetch, "images", "inventory")
                    .order_by("-created_at")
                )
            return Product.objects.none()

        # For public listing, only show published products
        return (
            Product.objects.filter(status=Product.ProductStatus.PUBLISHED)
            .select_related("category", "brand")
            .prefetch_related(primary_image_prefetch)
        )

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "retrieve" or self.action == "my_products":
            return ProductDetailSerializer
        return ProductListSerializer

    def perform_create(self, serializer):
        """Set shopkeeper as product owner when creating"""
        serializer.save(shopkeeper=self.request.user)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="my-products",
    )
    def my_products(self, request: Request) -> Response:
        """
        Get all products owned by the authenticated shopkeeper.

        Includes products with ALL statuses (DRAFT, PUBLISHED, etc.)

        GET /api/products/my-products/

        Query params:
        - page: Page number
        - page_size: Items per page (default: 10)
        - status: Filter by status (DRAFT, PUBLISHED, etc.)
        - search: Search in name, description, SKU
        - ordering: Sort by price, created_at, name

        Returns:
            Paginated list of shopkeeper's products
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Optional status filter
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
