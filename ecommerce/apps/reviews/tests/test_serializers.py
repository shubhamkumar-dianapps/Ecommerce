"""
Reviews App Serializer Tests

Comprehensive tests for review serializers.
"""

from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from apps.reviews.serializers.review import (
    ReviewListSerializer,
    ReviewDetailSerializer,
    ReviewCreateUpdateSerializer,
    ReviewReplySerializer,
)
from apps.reviews.tests.factories import (
    UserFactory,
    ProductFactory,
    ReviewFactory,
)


class ReviewListSerializerTest(TestCase):
    """Tests for ReviewListSerializer."""

    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.shopkeeper = UserFactory.create_shopkeeper()
        self.product = ProductFactory.create_product(shopkeeper=self.shopkeeper)
        self.customer = UserFactory.create_customer()

    def test_serialization(self):
        """Test basic serialization."""
        review = ReviewFactory.create_review(
            product=self.product,
            user=self.customer,
            rating=Decimal("4.5"),
        )

        serializer = ReviewListSerializer(review)
        data = serializer.data

        self.assertEqual(data["rating"], "4.5")
        self.assertEqual(data["product"], self.product.id)
        self.assertIn("helpful_count", data)
        self.assertIn("user_name", data)

    def test_user_has_liked_authenticated(self):
        """Test user_has_liked with authenticated user."""
        review = ReviewFactory.create_review(product=self.product)
        ReviewFactory.create_like(review=review, user=self.customer)

        request = self.factory.get("/")
        request.user = self.customer

        serializer = ReviewListSerializer(review, context={"request": request})

        self.assertTrue(serializer.data["user_has_liked"])

    def test_user_has_liked_not_liked(self):
        """Test user_has_liked when user hasn't liked."""
        review = ReviewFactory.create_review(product=self.product)

        request = self.factory.get("/")
        request.user = self.customer

        serializer = ReviewListSerializer(review, context={"request": request})

        self.assertFalse(serializer.data["user_has_liked"])

    def test_reply_count(self):
        """Test reply_count calculation."""
        review = ReviewFactory.create_review(product=self.product)

        # Create 2 active and 1 inactive replies
        ReviewFactory.create_reply(review=review, is_active=True)
        ReviewFactory.create_reply(review=review, is_active=True)
        ReviewFactory.create_reply(review=review, is_active=False)

        serializer = ReviewListSerializer(review)

        self.assertEqual(serializer.data["reply_count"], 2)


class ReviewDetailSerializerTest(TestCase):
    """Tests for ReviewDetailSerializer."""

    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.shopkeeper = UserFactory.create_shopkeeper()
        self.product = ProductFactory.create_product(shopkeeper=self.shopkeeper)

    def test_includes_replies(self):
        """Test that detail serializer includes replies."""
        review = ReviewFactory.create_review(product=self.product)
        ReviewFactory.create_reply(review=review, is_active=True)
        ReviewFactory.create_reply(review=review, is_active=True)

        request = self.factory.get("/")
        request.user = UserFactory.create_customer()  # Add user to request
        serializer = ReviewDetailSerializer(review, context={"request": request})

        self.assertIn("replies", serializer.data)
        self.assertEqual(len(serializer.data["replies"]), 2)

    def test_excludes_inactive_replies(self):
        """Test that inactive replies are excluded."""
        review = ReviewFactory.create_review(product=self.product)
        ReviewFactory.create_reply(review=review, is_active=True)
        ReviewFactory.create_reply(review=review, is_active=False)

        request = self.factory.get("/")
        request.user = UserFactory.create_customer()  # Add user to request
        serializer = ReviewDetailSerializer(review, context={"request": request})

        self.assertEqual(len(serializer.data["replies"]), 1)

    def test_includes_likes(self):
        """Test that detail serializer includes likes."""
        review = ReviewFactory.create_review(product=self.product)
        customer1 = UserFactory.create_customer()
        customer2 = UserFactory.create_customer()
        ReviewFactory.create_like(review=review, user=customer1)
        ReviewFactory.create_like(review=review, user=customer2)

        serializer = ReviewDetailSerializer(review)

        self.assertIn("likes", serializer.data)
        self.assertEqual(len(serializer.data["likes"]), 2)


class ReviewCreateUpdateSerializerTest(TestCase):
    """Tests for ReviewCreateUpdateSerializer."""

    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.shopkeeper = UserFactory.create_shopkeeper()
        self.product = ProductFactory.create_product(shopkeeper=self.shopkeeper)
        self.customer = UserFactory.create_customer()

    def test_valid_rating(self):
        """Test validation with valid rating."""
        request = self.factory.post("/")
        request.user = self.customer

        data = {
            "product": self.product.id,
            "rating": "4.5",
            "title": "Great Product",
            "comment": "This is an excellent product!",
        }
        serializer = ReviewCreateUpdateSerializer(
            data=data, context={"request": request}
        )

        self.assertTrue(serializer.is_valid())

    def test_invalid_rating_below_min(self):
        """Test validation rejects rating below minimum."""
        request = self.factory.post("/")
        request.user = self.customer

        data = {
            "product": self.product.id,
            "rating": "0.5",
            "title": "Bad Rating",
            "comment": "Testing invalid rating",
        }
        serializer = ReviewCreateUpdateSerializer(
            data=data, context={"request": request}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)

    def test_invalid_rating_above_max(self):
        """Test validation rejects rating above maximum."""
        request = self.factory.post("/")
        request.user = self.customer

        data = {
            "product": self.product.id,
            "rating": "6.0",
            "title": "Bad Rating",
            "comment": "Testing invalid rating",
        }
        serializer = ReviewCreateUpdateSerializer(
            data=data, context={"request": request}
        )

        self.assertFalse(serializer.is_valid())

    def test_invalid_rating_not_half_increment(self):
        """Test validation rejects non-0.5 increment ratings."""
        request = self.factory.post("/")
        request.user = self.customer

        data = {
            "product": self.product.id,
            "rating": "4.3",
            "title": "Bad Rating",
            "comment": "Testing invalid rating increment",
        }
        serializer = ReviewCreateUpdateSerializer(
            data=data, context={"request": request}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)

    def test_duplicate_review_rejected(self):
        """Test that duplicate review is rejected."""
        # Create existing review
        ReviewFactory.create_review(product=self.product, user=self.customer)

        request = self.factory.post("/")
        request.user = self.customer

        data = {
            "product": self.product.id,
            "rating": "5.0",
            "title": "Duplicate Review",
            "comment": "Trying to submit duplicate!",
        }
        serializer = ReviewCreateUpdateSerializer(
            data=data, context={"request": request}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_create_sets_user(self):
        """Test that create sets user from request."""
        request = self.factory.post("/")
        request.user = self.customer

        data = {
            "product": self.product.id,
            "rating": "4.5",
            "title": "Great Product",
            "comment": "This is an excellent product!",
        }
        serializer = ReviewCreateUpdateSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid()
        review = serializer.save()

        self.assertEqual(review.user, self.customer)


class ReviewReplySerializerTest(TestCase):
    """Tests for ReviewReplySerializer."""

    def setUp(self):
        """Set up test data."""
        self.shopkeeper = UserFactory.create_shopkeeper()
        self.product = ProductFactory.create_product(shopkeeper=self.shopkeeper)
        self.review = ReviewFactory.create_review(product=self.product)

    def test_is_product_owner_true(self):
        """Test is_product_owner is True for product owner."""
        reply = ReviewFactory.create_reply(
            review=self.review,
            user=self.shopkeeper,  # Product owner
        )

        serializer = ReviewReplySerializer(reply)

        self.assertTrue(serializer.data["is_product_owner"])

    def test_is_product_owner_false(self):
        """Test is_product_owner is False for non-owner."""
        other_shopkeeper = UserFactory.create_shopkeeper()
        reply = ReviewFactory.create_reply(
            review=self.review,
            user=other_shopkeeper,
        )

        serializer = ReviewReplySerializer(reply)

        self.assertFalse(serializer.data["is_product_owner"])
