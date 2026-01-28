"""
Pagination Classes for Accounts App

Custom pagination configurations for different endpoint types.
"""

from rest_framework.pagination import PageNumberPagination
from apps.accounts import constants


class AccountsPagination(PageNumberPagination):
    """
    Standard pagination for accounts endpoints.

    Configurable page size with reasonable defaults.
    """

    page_size = constants.DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = constants.MAX_PAGE_SIZE


class AuditLogPagination(PageNumberPagination):
    """
    Pagination for audit log listings.

    Larger page size for admin review.
    """

    page_size = constants.AUDIT_LOG_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = constants.MAX_PAGE_SIZE


class SessionPagination(PageNumberPagination):
    """
    Pagination for session listings.

    Smaller page size for better UX.
    """

    page_size = constants.SESSION_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = constants.MAX_PAGE_SIZE
