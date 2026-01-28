"""
Products Pagination

Pagination classes for products app using constants.
"""

from rest_framework.pagination import PageNumberPagination
from apps.products import constants


class ProductPagination(PageNumberPagination):
    """
    Pagination for product listings.

    Default: 12 items per page (good for grid layouts)
    Max: 50 items per page
    """

    page_size = constants.PRODUCT_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = constants.PRODUCT_MAX_PAGE_SIZE
    page_query_param = "page"


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
