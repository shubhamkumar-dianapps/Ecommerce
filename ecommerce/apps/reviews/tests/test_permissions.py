"""
Reviews App Permission Tests

Comprehensive tests for review permission classes.
"""

from django.test import TestCase
from rest_framework.test import APIRequestFactory
from apps.reviews.permissions import (
    IsReviewOwnerOrReadOnly,
    CanReplyToReview,
    IsReplyOwnerOrReadOnly,
)
from apps.reviews.tests.factories import (
    UserFactory,
    ProductFactory,
    ReviewFactory,
)


class MockView:
    """Mock view for testing permissions."""

    pass


class IsReviewOwnerOrReadOnlyTest(TestCase):
    """Tests for IsReviewOwnerOrReadOnly permission."""

    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.permission = IsReviewOwnerOrReadOnly()
        self.view = MockView()
        self.review = ReviewFactory.create_review()

    def test_safe_methods_allowed_for_anyone(self):
        """Test that GET requests are allowed for anyone."""
        request = self.factory.get("/")
        request.user = None  # Anonymous user

        result = self.permission.has_object_permission(request, self.view, self.review)

        self.assertTrue(result)

    def test_owner_can_modify(self):
        """Test that review owner can modify."""
        request = self.factory.put("/")
        request.user = self.review.user

        result = self.permission.has_object_permission(request, self.view, self.review)

        self.assertTrue(result)

    def test_non_owner_cannot_modify(self):
        """Test that non-owner cannot modify."""
        other_user = UserFactory.create_customer()
        request = self.factory.put("/")
        request.user = other_user

        result = self.permission.has_object_permission(request, self.view, self.review)

        self.assertFalse(result)


class CanReplyToReviewTest(TestCase):
    """Tests for CanReplyToReview permission."""

    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.permission = CanReplyToReview()
        self.view = MockView()

    def test_admin_can_reply(self):
        """Test that admin users can reply."""
        admin = UserFactory.create_admin()
        request = self.factory.post("/")
        request.user = admin

        result = self.permission.has_permission(request, self.view)

        self.assertTrue(result)

    def test_verified_shopkeeper_can_reply(self):
        """Test that verified shopkeepers can reply."""
        shopkeeper = UserFactory.create_shopkeeper(is_verified=True)
        request = self.factory.post("/")
        request.user = shopkeeper

        result = self.permission.has_permission(request, self.view)

        self.assertTrue(result)

    def test_unverified_shopkeeper_cannot_reply(self):
        """Test that unverified shopkeepers cannot reply."""
        shopkeeper = UserFactory.create_shopkeeper(is_verified=False)
        request = self.factory.post("/")
        request.user = shopkeeper

        result = self.permission.has_permission(request, self.view)

        self.assertFalse(result)

    def test_customer_cannot_reply(self):
        """Test that regular customers cannot reply."""
        customer = UserFactory.create_customer()
        request = self.factory.post("/")
        request.user = customer

        result = self.permission.has_permission(request, self.view)

        self.assertFalse(result)

    def test_anonymous_cannot_reply(self):
        """Test that anonymous users cannot reply."""
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.post("/")
        request.user = AnonymousUser()

        result = self.permission.has_permission(request, self.view)

        self.assertFalse(result)


class IsReplyOwnerOrReadOnlyTest(TestCase):
    """Tests for IsReplyOwnerOrReadOnly permission."""

    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.permission = IsReplyOwnerOrReadOnly()
        self.view = MockView()
        self.shopkeeper = UserFactory.create_shopkeeper()
        self.product = ProductFactory.create_product(shopkeeper=self.shopkeeper)
        self.review = ReviewFactory.create_review(product=self.product)
        self.reply = ReviewFactory.create_reply(
            review=self.review, user=self.shopkeeper
        )

    def test_safe_methods_allowed_for_anyone(self):
        """Test that GET requests are allowed for anyone."""
        request = self.factory.get("/")
        request.user = None

        result = self.permission.has_object_permission(request, self.view, self.reply)

        self.assertTrue(result)

    def test_owner_can_modify(self):
        """Test that reply owner can modify."""
        request = self.factory.put("/")
        request.user = self.shopkeeper

        result = self.permission.has_object_permission(request, self.view, self.reply)

        self.assertTrue(result)

    def test_non_owner_cannot_modify(self):
        """Test that non-owner cannot modify."""
        other_user = UserFactory.create_shopkeeper()
        request = self.factory.put("/")
        request.user = other_user

        result = self.permission.has_object_permission(request, self.view, self.reply)

        self.assertFalse(result)
