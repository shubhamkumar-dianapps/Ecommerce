"""
Reviews App Model Tests

Comprehensive tests for Review, ReviewLike, and ReviewReply models.
"""

from decimal import Decimal
from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from apps.reviews.models import Review, ReviewLike, ReviewReply
from apps.reviews.tests.factories import (
    UserFactory,
    ProductFactory,
    ReviewFactory,
)


class ReviewModelTest(TestCase):
    """Tests for Review model."""

    def setUp(self):
        """Set up test data."""
        self.shopkeeper = UserFactory.create_shopkeeper()
        self.customer = UserFactory.create_customer()
        self.product = ProductFactory.create_product(shopkeeper=self.shopkeeper)

    def test_create_review_success(self):
        """Test creating a valid review."""
        review = Review.objects.create(
            product=self.product,
            user=self.customer,
            rating=Decimal("4.5"),
            title="Great Product",
            comment="This is an excellent product, highly recommended!",
        )

        self.assertEqual(review.rating, Decimal("4.5"))
        self.assertEqual(review.title, "Great Product")
        self.assertTrue(review.is_active)
        self.assertFalse(review.is_owner_review)
        self.assertEqual(review.helpful_count, 0)

    def test_owner_review_flag_set_automatically(self):
        """Test that is_owner_review is set for product owner."""
        review = Review.objects.create(
            product=self.product,
            user=self.shopkeeper,  # Product owner
            rating=Decimal("5.0"),
            title="Owner Review",
            comment="As the owner, I can vouch for this product quality.",
        )

        self.assertTrue(review.is_owner_review)

    def test_unique_constraint_product_user(self):
        """Test that user can only review a product once."""
        Review.objects.create(
            product=self.product,
            user=self.customer,
            rating=Decimal("4.0"),
            title="First Review",
            comment="Great product!",
        )

        with self.assertRaises(IntegrityError):
            Review.objects.create(
                product=self.product,
                user=self.customer,
                rating=Decimal("5.0"),
                title="Second Review",
                comment="Trying to review again!",
            )

    def test_rating_validation_min(self):
        """Test that rating below minimum is rejected."""
        review = Review(
            product=self.product,
            user=self.customer,
            rating=Decimal("0.5"),  # Below minimum of 1
            title="Bad Rating",
            comment="Testing invalid rating",
        )

        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_rating_validation_max(self):
        """Test that rating above maximum is rejected."""
        review = Review(
            product=self.product,
            user=self.customer,
            rating=Decimal("6.0"),  # Above maximum of 5
            title="Bad Rating",
            comment="Testing invalid rating",
        )

        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_rating_validation_half_increments(self):
        """Test that only 0.5 increments are allowed."""
        # Valid rating
        review_valid = Review(
            product=self.product,
            user=self.customer,
            rating=Decimal("3.5"),
            title="Valid Rating",
            comment="Testing valid rating",
        )
        review_valid.full_clean()  # Should not raise

        # Create new customer for second review
        customer2 = UserFactory.create_customer()

        # Invalid rating (0.3 not allowed)
        review_invalid = Review(
            product=self.product,
            user=customer2,
            rating=Decimal("3.3"),
            title="Invalid Rating",
            comment="Testing invalid rating",
        )

        with self.assertRaises(ValidationError):
            review_invalid.full_clean()

    def test_increment_helpful_count(self):
        """Test increment_helpful_count method."""
        review = ReviewFactory.create_review(
            product=self.product,
            user=self.customer,
        )

        self.assertEqual(review.helpful_count, 0)
        review.increment_helpful_count()
        self.assertEqual(review.helpful_count, 1)
        review.increment_helpful_count()
        self.assertEqual(review.helpful_count, 2)

    def test_decrement_helpful_count(self):
        """Test decrement_helpful_count method."""
        review = ReviewFactory.create_review(
            product=self.product,
            user=self.customer,
        )
        review.helpful_count = 5
        review.save()

        review.decrement_helpful_count()
        self.assertEqual(review.helpful_count, 4)

    def test_decrement_helpful_count_not_below_zero(self):
        """Test that helpful_count doesn't go below zero."""
        review = ReviewFactory.create_review(
            product=self.product,
            user=self.customer,
        )

        self.assertEqual(review.helpful_count, 0)
        review.decrement_helpful_count()
        self.assertEqual(review.helpful_count, 0)  # Should stay at 0

    def test_str_representation(self):
        """Test __str__ method."""
        review = ReviewFactory.create_review(
            product=self.product,
            user=self.customer,
            rating=Decimal("4.0"),
        )

        expected = f"{self.customer.email} - {self.product.name} (4.0/5)"
        self.assertEqual(str(review), expected)


class ReviewLikeModelTest(TestCase):
    """Tests for ReviewLike model."""

    def setUp(self):
        """Set up test data."""
        self.review = ReviewFactory.create_review()
        self.user = UserFactory.create_customer()

    def test_create_like_success(self):
        """Test creating a valid like."""
        like = ReviewLike.objects.create(
            review=self.review,
            user=self.user,
        )

        self.assertEqual(like.review, self.review)
        self.assertEqual(like.user, self.user)
        self.assertIsNotNone(like.created_at)

    def test_unique_constraint_review_user(self):
        """Test that user can only like a review once."""
        ReviewLike.objects.create(
            review=self.review,
            user=self.user,
        )

        with self.assertRaises(IntegrityError):
            ReviewLike.objects.create(
                review=self.review,
                user=self.user,
            )

    def test_str_representation(self):
        """Test __str__ method."""
        like = ReviewLike.objects.create(
            review=self.review,
            user=self.user,
        )

        expected = f"{self.user.email} liked review by {self.review.user.email}"
        self.assertEqual(str(like), expected)


class ReviewReplyModelTest(TestCase):
    """Tests for ReviewReply model."""

    def setUp(self):
        """Set up test data."""
        self.shopkeeper = UserFactory.create_shopkeeper()
        self.product = ProductFactory.create_product(shopkeeper=self.shopkeeper)
        self.review = ReviewFactory.create_review(product=self.product)

    def test_create_reply_success(self):
        """Test creating a valid reply."""
        reply = ReviewReply.objects.create(
            review=self.review,
            user=self.shopkeeper,
            comment="Thank you for your review!",
        )

        self.assertEqual(reply.review, self.review)
        self.assertEqual(reply.user, self.shopkeeper)
        self.assertTrue(reply.is_active)

    def test_reply_ordering(self):
        """Test that replies are ordered oldest first."""
        reply1 = ReviewFactory.create_reply(
            review=self.review,
            user=self.shopkeeper,
            comment="First reply",
        )
        reply2 = ReviewFactory.create_reply(
            review=self.review,
            user=self.shopkeeper,
            comment="Second reply",
        )

        replies = list(self.review.replies.all())
        self.assertEqual(replies[0], reply1)
        self.assertEqual(replies[1], reply2)

    def test_str_representation(self):
        """Test __str__ method."""
        reply = ReviewReply.objects.create(
            review=self.review,
            user=self.shopkeeper,
            comment="Test reply",
        )

        expected = f"Reply by {self.shopkeeper.email} to review {self.review.id}"
        self.assertEqual(str(reply), expected)
