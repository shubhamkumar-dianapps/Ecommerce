"""
Reviews App Pagination

Pagination classes for reviews and replies using CursorPagination.
"""

from rest_framework.pagination import CursorPagination
from apps.reviews import constants


class ReviewPagination(CursorPagination):
    """
    Cursor-based pagination for product reviews.

    Benefits:
    - Better performance on large datasets (no OFFSET)
    - Consistent results during infinite scroll
    - No duplicate/skipped reviews when new ones are added

    Default: 10 reviews per page
    Maximum: 50 reviews per page
    """

    page_size = constants.DEFAULT_REVIEWS_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = constants.MAX_REVIEWS_PAGE_SIZE
    ordering = "-created_at"  # Required for cursor pagination
    cursor_query_param = "cursor"


class ReplyPagination(CursorPagination):
    """
    Cursor-based pagination for review replies.

    Default: 5 replies per page
    Maximum: 20 replies per page
    """

    page_size = constants.DEFAULT_REPLIES_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = constants.MAX_REPLIES_PAGE_SIZE
    ordering = "created_at"  # Oldest replies first
    cursor_query_param = "cursor"
