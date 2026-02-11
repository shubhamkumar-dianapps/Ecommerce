"""
Product Views

Production-ready views with proper permissions, pagination, and filtering.
"""

import environ
from rest_framework import viewsets, permissions, filters, status
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
from apps.products.filters import ProductFilter
from apps.products.pagination import (
    ProductPagination,
    CategoryPagination,
    BrandPagination,
)

env = environ.Env()


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

    def list(self, request, *args, **kwargs):
        """List categories with Redis caching (1 hour TTL)."""
        from apps.core.cache_utils import cache_logger

        cache_key = "categories:list:all"
        cached_data = cache_logger.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        # Cache miss - fetch from DB
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            response_data = serializer.data

        # Cache for 1 hour (3600 seconds)
        cache_logger.set(cache_key, response_data, timeout=env("CACHE_TIMEOUT"))
        return Response(response_data)


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

    def list(self, request, *args, **kwargs):
        """List brands with Redis caching (1 hour TTL)."""
        from apps.core.cache_utils import cache_logger

        cache_key = "brands:list:all"
        cached_data = cache_logger.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        # Cache miss - fetch from DB
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            response_data = serializer.data

        # Cache for configured timeout
        cache_logger.set(cache_key, response_data, timeout=env.int("CACHE_TIMEOUT"))
        return Response(response_data)


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
    filterset_class = ProductFilter  # Use custom filter with slug support
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
        if self.action in ["create", "update", "partial_update"]:
            from apps.products.serializers import ProductCreateUpdateSerializer

            return ProductCreateUpdateSerializer
        if self.action == "retrieve" or self.action == "my_products":
            return ProductDetailSerializer
        return ProductListSerializer

    def list(self, request, *args, **kwargs):
        """List products with Redis caching (5 min TTL)."""
        from apps.core.cache_utils import cache_logger

        # Build cache key from query params
        query_params = request.query_params.dict()
        cache_key = f"products:list:{hash(frozenset(query_params.items()))}"
        cached_data = cache_logger.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        # Cache miss - fetch from DB
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            response_data = serializer.data

        # Cache for configured timeout
        cache_logger.set(cache_key, response_data, timeout=env.int("CACHE_TIMEOUT"))
        return Response(response_data)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve product detail with Redis caching (10 min TTL)."""
        from apps.core.cache_utils import cache_logger

        slug = kwargs.get("slug")
        cache_key = f"products:detail:{slug}"
        cached_data = cache_logger.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        # Cache miss - fetch from DB
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = serializer.data

        # Cache for configured timeout
        cache_logger.set(cache_key, response_data, timeout=env.int("CACHE_TIMEOUT"))
        return Response(response_data)

    def perform_create(self, serializer):
        """Set shopkeeper as product owner and invalidate cache"""
        from apps.core.cache_utils import cache_logger

        serializer.save(shopkeeper=self.request.user)
        # Invalidate product list cache
        cache_logger.invalidate_pattern("products:list:*")

    def perform_update(self, serializer):
        """Update product and invalidate cache"""
        from apps.core.cache_utils import cache_logger

        instance = serializer.save()
        # Invalidate both list and detail cache
        cache_logger.invalidate_pattern("products:list:*")
        cache_logger.delete(f"products:detail:{instance.slug}")

    def perform_destroy(self, instance):
        """Delete product and invalidate cache"""
        from apps.core.cache_utils import cache_logger

        slug = instance.slug
        instance.delete()
        # Invalidate both list and detail cache
        cache_logger.invalidate_pattern("products:list:*")
        cache_logger.delete(f"products:detail:{slug}")

    def destroy(self, request, *args, **kwargs):
        """Delete product with confirmation message."""
        instance = self.get_object()
        product_name = instance.name
        self.perform_destroy(instance)
        return Response(
            {"detail": f"Product '{product_name}' has been deleted successfully."},
            status=status.HTTP_200_OK,
        )

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
