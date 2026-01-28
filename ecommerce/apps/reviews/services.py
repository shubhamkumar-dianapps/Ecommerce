"""
Review Service

Business logic for review operations.
"""

from typing import Tuple
from django.db import transaction
from apps.reviews.models import Review, ReviewLike


class ReviewService:
    """Service class for review operations."""

    @staticmethod
    @transaction.atomic
    def toggle_like(review: Review, user) -> Tuple[bool, int]:
        """
        Toggle like on a review.

        If user already liked the review, removes the like.
        If user hasn't liked, adds a like.

        Args:
            review: Review instance
            user: User instance

        Returns:
            Tuple of (liked, helpful_count) where:
            - liked: True if like was added, False if removed
            - helpful_count: Updated helpful count
        """
        existing_like = ReviewLike.objects.filter(review=review, user=user).first()

        if existing_like:
            # Unlike: Remove like and decrement count
            existing_like.delete()
            review.decrement_helpful_count()
            liked = False
        else:
            # Like: Add like and increment count
            ReviewLike.objects.create(review=review, user=user)
            review.increment_helpful_count()
            liked = True

        # Refresh to get updated count
        review.refresh_from_db()

        return liked, review.helpful_count

    @staticmethod
    def get_user_reviews(user, include_inactive: bool = True):
        """
        Get all reviews by a user.

        Args:
            user: User instance
            include_inactive: Whether to include inactive reviews

        Returns:
            QuerySet of user's reviews
        """
        queryset = (
            Review.objects.filter(user=user)
            .select_related("product", "user")
            .prefetch_related("likes", "replies")
        )

        if not include_inactive:
            queryset = queryset.filter(is_active=True)

        return queryset.order_by("-created_at")

    @staticmethod
    def get_product_reviews(product_id: int, only_active: bool = True):
        """
        Get all reviews for a product.

        Args:
            product_id: Product ID
            only_active: Whether to only return active reviews

        Returns:
            QuerySet of product reviews
        """
        queryset = (
            Review.objects.filter(product_id=product_id)
            .select_related("product", "user")
            .prefetch_related("likes", "replies")
        )

        if only_active:
            queryset = queryset.filter(is_active=True)

        return queryset.order_by("-created_at")

    @staticmethod
    def check_user_can_review(user, product) -> Tuple[bool, str]:
        """
        Check if a user can review a product.

        Customers can only review products they have purchased.
        Product owners cannot review their own products.

        Args:
            user: User instance
            product: Product instance

        Returns:
            Tuple of (can_review, reason)
        """
        # Product owner cannot review their own product
        if product.shopkeeper == user:
            return False, "You cannot review your own product"

        # Check if user has already reviewed this product
        if Review.objects.filter(user=user, product=product).exists():
            return False, "You have already reviewed this product"

        # Check if customer has purchased the product
        from apps.orders.models import Order, OrderItem
        from apps.accounts.models import User

        if user.role == User.Role.CUSTOMER:
            has_purchased = OrderItem.objects.filter(
                order__user=user,
                order__status=Order.OrderStatus.DELIVERED,
                product=product,
            ).exists()

            if not has_purchased:
                return False, "You can only review products you have purchased"

        return True, ""
