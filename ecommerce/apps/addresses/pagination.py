"""
Address Pagination

Pagination classes for address listings.
"""

from rest_framework.pagination import PageNumberPagination
from apps.addresses import constants


class AddressPagination(PageNumberPagination):
    """
    Standard pagination for address listings.

    Features:
    - Default page size from constants
    - Configurable via ?page_size query parameter
    - Max page size limit for performance
    """

    page_size = constants.DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = constants.MAX_PAGE_SIZE
