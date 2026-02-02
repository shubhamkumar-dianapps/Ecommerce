"""
Products Pagination

Pagination classes for products app using CursorPagination for performance.
"""

from rest_framework.pagination import CursorPagination, PageNumberPagination
from apps.products import constants


class ProductPagination(CursorPagination):
    """
    Cursor-based pagination for product listings.

    Benefits:
    - Better performance on large datasets (no OFFSET)
    - Consistent results during infinite scroll
    - No duplicate/skipped items when data changes

    Default: 12 items per page (good for grid layouts)
    """

    page_size = constants.PRODUCT_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = constants.PRODUCT_MAX_PAGE_SIZE
    ordering = "-created_at"  # Required for cursor pagination
    cursor_query_param = "cursor"


class CategoryPagination(PageNumberPagination):
    """
    Pagination for category listings.

    Default: 20 items per page
    Max: 100 items per page
    """

    page_size = constants.CATEGORY_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = constants.CATEGORY_MAX_PAGE_SIZE
    page_query_param = "page"


class BrandPagination(PageNumberPagination):
    """
    Pagination for brand listings.

    Default: 20 items per page
    Max: 100 items per page
    """

    page_size = constants.BRAND_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = constants.BRAND_MAX_PAGE_SIZE
    page_query_param = "page"
