"""
Reviews App Models

Production-ready models for reviews, likes, and replies with comprehensive features.
"""

from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.models import TimeStampedModel
from apps.products.models import Product
from apps.reviews import constants
from apps.reviews.validators import (
    validate_rating,
    validate_review_title_length,
    validate_review_comment_length,
    validate_reply_comment_length,
)


class Review(TimeStampedModel):
    """
    Product Review Model

    Stores customer and shopkeeper reviews for products with ratings.

    Features:
    - 1-5 star ratings (0.5 increments)
    - Title and detailed comment
    - Admin moderation (is_active)
    - Owner review flagging
    - Helpful count (denormalized)
    - Unique constraint: one review per user per product

    Relationships:
    - Product: Many reviews per product
    - User: Many reviews per user
    - ReviewLike: Many likes per review
    - ReviewReply: Many replies per review
    """

    # Relationships
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        help_text="Product being reviewed",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        help_text="User who wrote the review",
    )

    # Content
    rating = models.DecimalField(
        max_digits=constants.RATING_MAX_DIGITS,
        decimal_places=constants.RATING_DECIMAL_PLACES,
        validators=[
            MinValueValidator(Decimal(str(constants.MIN_RATING))),
            MaxValueValidator(Decimal(str(constants.MAX_RATING))),
            validate_rating,
        ],
        help_text=f"Rating from {constants.MIN_RATING} to {constants.MAX_RATING} (0.5 increments)",
    )
    title = models.CharField(
        max_length=constants.REVIEW_TITLE_MAX_LENGTH,
        validators=[validate_review_title_length],
        help_text="Short review title",
    )
    comment = models.TextField(
        max_length=constants.REVIEW_COMMENT_MAX_LENGTH,
        validators=[validate_review_comment_length],
        help_text="Detailed review comment",
    )

    # Status and Flags
    is_active = models.BooleanField(
        default=True,
        help_text="Admin can deactivate vulgar or inappropriate reviews",
    )
    is_verified_purchase = models.BooleanField(
        default=False,
        help_text="Whether user actually purchased this product",
    )
    is_owner_review = models.BooleanField(
        default=False,
        help_text="True if review is from product owner",
    )

    # Denormalized Fields
    helpful_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of users who found this review helpful (liked it)",
    )

    class Meta:
        db_table = "reviews"
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-created_at"]
        unique_together = [["product", "user"]]
        indexes = [
            models.Index(fields=["product", "-created_at"]),
            models.Index(fields=["product", "-rating"]),
            models.Index(fields=["product", "-helpful_count"]),
            models.Index(fields=["is_active", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} - {self.product.name} ({self.rating}/5)"

    def save(self, *args, **kwargs):
        """Override save to set is_owner_review flag"""
        # Check if user is the product owner
        if self.product.shopkeeper == self.user:
            self.is_owner_review = True
        super().save(*args, **kwargs)

    def increment_helpful_count(self) -> None:
        """Increment helpful count when review is liked"""
        self.helpful_count = models.F("helpful_count") + 1
        self.save(update_fields=["helpful_count"])
        self.refresh_from_db()

    def decrement_helpful_count(self) -> None:
        """Decrement helpful count when like is removed"""
        if self.helpful_count > 0:
            self.helpful_count = models.F("helpful_count") - 1
            self.save(update_fields=["helpful_count"])
            self.refresh_from_db()


class ReviewLike(TimeStampedModel):
    """
    Review Like Model

    Tracks which users found a review helpful.

    Features:
    - One like per user per review
    - Timestamps for analytics

    Relationships:
    - Review: Many likes per review
    - User: Many likes per user
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="likes",
        help_text="Review being liked",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="review_likes",
        help_text="User who liked the review",
    )

    class Meta:
        db_table = "review_likes"
        verbose_name = "Review Like"
        verbose_name_plural = "Review Likes"
        ordering = ["-created_at"]
        unique_together = [["review", "user"]]
        indexes = [
            models.Index(fields=["review", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} liked review by {self.review.user.email}"


class ReviewReply(TimeStampedModel):
    """
    Review Reply Model

    Allows product owners and verified shopkeepers to reply to reviews.

    Features:
    - Admin moderation (is_active)
    - Edit tracking (updated_at)

    Permissions:
    - Product owner can reply
    - Verified shopkeepers can reply
    - Regular customers cannot reply

    Relationships:
    - Review: Many replies per review
    - User: Many replies per user
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="replies",
        help_text="Review being replied to",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="review_replies",
        help_text="User who wrote the reply",
    )
    comment = models.TextField(
        max_length=constants.REPLY_COMMENT_MAX_LENGTH,
        validators=[validate_reply_comment_length],
        help_text="Reply comment",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Admin can deactivate inappropriate replies",
    )

    class Meta:
        db_table = "review_replies"
        verbose_name = "Review Reply"
        verbose_name_plural = "Review Replies"
        ordering = ["created_at"]  # Oldest first for chronological reading
        indexes = [
            models.Index(fields=["review", "created_at"]),
            models.Index(fields=["is_active", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Reply by {self.user.email} to review {self.review.id}"
