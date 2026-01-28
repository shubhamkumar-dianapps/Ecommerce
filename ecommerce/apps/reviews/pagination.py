"""
Reviews App Pagination

Pagination classes for reviews and replies.
"""

from rest_framework.pagination import PageNumberPagination
from apps.reviews import constants


class ReviewPagination(PageNumberPagination):
    """
    Pagination for product reviews.

    Default: 10 reviews per page
    Maximum: 50 reviews per page
    """

    page_size = constants.DEFAULT_REVIEWS_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = constants.MAX_REVIEWS_PAGE_SIZE


class ReplyPagination(PageNumberPagination):
    """
    Pagination for review replies.

    Default: 5 replies per page
    Maximum: 20 replies per page
    """

    page_size = constants.DEFAULT_REPLIES_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = constants.MAX_REPLIES_PAGE_SIZE
