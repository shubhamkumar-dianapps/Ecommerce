"""
Review Views

Production-ready views for reviews with comprehensive features.
"""

from django.db.models import QuerySet
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.reviews.models import Review
from apps.reviews.serializers.review import (
    ReviewListSerializer,
    ReviewDetailSerializer,
    ReviewCreateUpdateSerializer,
    ReviewReplySerializer,
)
from apps.reviews.permissions import (
    IsReviewOwnerOrReadOnly,
    CanReplyToReview,
)
from apps.reviews.pagination import ReviewPagination
from apps.reviews.services import ReviewService
from apps.reviews import constants


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Review ViewSet

    Endpoints:
    - GET /api/products/{product_id}/reviews/ - List product reviews
    - GET /api/products/{product_id}/reviews/{id}/ - Get review details
    - POST /api/products/{product_id}/reviews/ - Create review
    - PUT/PATCH /api/products/{product_id}/reviews/{id}/ - Update own review
    - DELETE /api/products/{product_id}/reviews/{id}/ - Delete own review

    Custom Actions:
    - POST /api/products/{product_id}/reviews/{id}/like/ - Toggle like
    - POST /api/products/{product_id}/reviews/{id}/reply/ - Add reply
    - GET /api/reviews/my-reviews/ - Get user's own reviews

    Features:
    - Pagination (10 per page)
    - Filtering by rating, is_owner_review
    - Search in title and comment
    - Ordering by latest, highest rated, most liked
    - Only active reviews shown to public
    - Users can only edit their own reviews
    - Like/unlike toggle
    - Replies from product owner and verified shopkeepers

    Permissions:
    - List/Retrieve: Anyone
    - Create: Authenticated users only
    - Update/Delete: Review owner only
    - Like: Authenticated users only
    - Reply: Product owner or verified shopkeepers only
    """

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsReviewOwnerOrReadOnly,
    ]
    pagination_class = ReviewPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["rating", "is_owner_review"]
    search_fields = ["title", "comment"]
    ordering_fields = ["created_at", "rating", "helpful_count"]
    ordering = ["-created_at"]

    def get_queryset(self) -> QuerySet[Review]:
        """
        Get queryset based on action.

        - Public listing: Only active reviews
        - My reviews: All user's reviews
        - Detail: All reviews (for owner access)
        """
        if self.action == "my_reviews":
            # User's own reviews (all statuses)
            if self.request.user.is_authenticated:
                return ReviewService.get_user_reviews(self.request.user)
            return Review.objects.none()

        # For public listing, show only active reviews
        queryset = (
            Review.objects.filter(is_active=True)
            .select_related("product", "user")
            .prefetch_related("likes", "replies")
        )

        # Filter by product if product_id in URL
        product_id = self.kwargs.get("product_id")
        if product_id:
            queryset = queryset.filter(product_id=product_id, is_active=True)

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ["create", "update", "partial_update"]:
            return ReviewCreateUpdateSerializer
        elif self.action == "retrieve" or self.action == "my_reviews":
            return ReviewDetailSerializer
        return ReviewListSerializer

    def perform_create(self, serializer):
        """Save review with user from request"""
        serializer.save(user=self.request.user)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="like",
    )
    def like(self, request: Request, pk=None, product_id=None) -> Response:
        """
        Toggle like on a review.

        POST /api/products/{product_id}/reviews/{id}/like/

        If user already liked the review, removes the like.
        If user hasn't liked, adds a like.

        Returns:
            Response with message and updated helpful_count
        """
        review = self.get_object()

        # Use service for business logic
        liked, helpful_count = ReviewService.toggle_like(review, request.user)

        message = constants.MSG_LIKE_ADDED if liked else constants.MSG_LIKE_REMOVED

        return Response(
            {
                "message": message,
                "liked": liked,
                "helpful_count": helpful_count,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, CanReplyToReview],
        url_path="reply",
    )
    def reply(self, request: Request, pk=None, product_id=None) -> Response:
        """
        Add a reply to a review.

        POST /api/products/{product_id}/reviews/{id}/reply/

        Body:
        {
            "comment": "Reply text"
        }

        Permissions:
        - Product owner can reply
        - Purchased Customer can reply

        Returns:
            Created reply data
        """
        review = self.get_object()

        serializer = ReviewReplySerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(review=review, user=request.user)

        return Response(
            {
                "message": constants.MSG_REPLY_CREATED,
                "reply": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated],
        url_path="my-reviews",
    )
    def my_reviews(self, request: Request) -> Response:
        """
        Get all reviews by the authenticated user.

        GET /api/reviews/my-reviews/

        Returns:
            Paginated list of user's reviews (all statuses)
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
