"""
Reviews App API Tests

Comprehensive tests for Review API endpoints.
"""

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.reviews.models import Review, ReviewReply
from apps.reviews.tests.factories import (
    UserFactory,
    ProductFactory,
    ReviewFactory,
)


class ReviewAPITestCase(TestCase):
    """Base test case with authentication helpers."""

    def setUp(self):
        """Set up test client and data."""
        self.client = APIClient()
        self.shopkeeper = UserFactory.create_shopkeeper()
        self.product = ProductFactory.create_product(shopkeeper=self.shopkeeper)
        self.customer = UserFactory.create_customer()

    def authenticate(self, user):
        """Authenticate the client with given user."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def get_reviews_url(self):
        """Get reviews list URL."""
        return reverse("reviews:review-list")

    def get_review_detail_url(self, review_id):
        """Get review detail URL."""
        return reverse("reviews:review-detail", kwargs={"pk": review_id})

    def get_review_like_url(self, review_id):
        """Get review like action URL."""
        return reverse("reviews:review-like", kwargs={"pk": review_id})

    def get_review_reply_url(self, review_id):
        """Get review reply action URL."""
        return reverse("reviews:review-reply", kwargs={"pk": review_id})

    def get_my_reviews_url(self):
        """Get my reviews URL."""
        return reverse("reviews:review-my-reviews")


class ReviewListCreateTest(ReviewAPITestCase):
    """Tests for review list and create endpoints."""

    def test_list_reviews_unauthenticated(self):
        """Test listing reviews without authentication."""
        ReviewFactory.create_review(product=self.product)

        response = self.client.get(self.get_reviews_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_reviews_only_active(self):
        """Test that only active reviews are listed."""
        ReviewFactory.create_review(product=self.product, is_active=True)
        ReviewFactory.create_review(product=self.product, is_active=False)  # Inactive

        response = self.client.get(self.get_reviews_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_review_authenticated(self):
        """Test creating a review as authenticated user."""
        self.authenticate(self.customer)

        data = {
            "product": str(self.product.id),
            "rating": "4.5",
            "title": "Great Product",
            "comment": "This is an excellent product. Really happy with my purchase!",
        }
        response = self.client.post(self.get_reviews_url(), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.first().rating, Decimal("4.5"))

    def test_create_review_unauthenticated(self):
        """Test that unauthenticated users cannot create reviews."""
        data = {
            "product": str(self.product.id),
            "rating": "4.5",
            "title": "Great Product",
            "comment": "This is an excellent product!",
        }
        response = self.client.post(self.get_reviews_url(), data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_duplicate_review_rejected(self):
        """Test that duplicate reviews are rejected."""
        self.authenticate(self.customer)

        # Create first review
        ReviewFactory.create_review(product=self.product, user=self.customer)

        # Try to create duplicate
        data = {
            "product": str(self.product.id),
            "rating": "5.0",
            "title": "Another Review",
            "comment": "Trying to submit another review!",
        }
        response = self.client.post(self.get_reviews_url(), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_reviews_by_rating(self):
        """Test filtering reviews by rating."""
        ReviewFactory.create_review(product=self.product, rating=Decimal("5.0"))
        customer2 = UserFactory.create_customer()
        ReviewFactory.create_review(
            product=self.product, user=customer2, rating=Decimal("3.0")
        )

        response = self.client.get(self.get_reviews_url(), {"rating": "5.0"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["rating"], "5.0")

    def test_order_reviews_by_helpful_count(self):
        """Test ordering reviews by helpful count."""
        review1 = ReviewFactory.create_review(product=self.product)
        review1.helpful_count = 10
        review1.save()

        customer2 = UserFactory.create_customer()
        review2 = ReviewFactory.create_review(product=self.product, user=customer2)
        review2.helpful_count = 50
        review2.save()

        response = self.client.get(
            self.get_reviews_url(), {"ordering": "-helpful_count"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["helpful_count"], 50)


class ReviewDetailUpdateDeleteTest(ReviewAPITestCase):
    """Tests for review detail, update, and delete endpoints."""

    def test_retrieve_review_detail(self):
        """Test retrieving review details."""
        review = ReviewFactory.create_review(product=self.product)

        response = self.client.get(self.get_review_detail_url(review.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], review.id)

    def test_update_own_review(self):
        """Test updating own review."""
        review = ReviewFactory.create_review(product=self.product, user=self.customer)
        self.authenticate(self.customer)

        data = {
            "product": str(self.product.id),
            "rating": "5.0",
            "title": "Updated Title",
            "comment": "Updated review comment with new information!",
        }
        response = self.client.put(self.get_review_detail_url(review.id), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.title, "Updated Title")

    def test_update_other_user_review_forbidden(self):
        """Test that users cannot update others' reviews."""
        other_customer = UserFactory.create_customer()
        review = ReviewFactory.create_review(product=self.product, user=other_customer)
        self.authenticate(self.customer)

        data = {
            "product": str(self.product.id),
            "rating": "1.0",
            "title": "Hacked Title",
            "comment": "Trying to modify someone else's review!",
        }
        response = self.client.put(self.get_review_detail_url(review.id), data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_review(self):
        """Test deleting own review."""
        review = ReviewFactory.create_review(product=self.product, user=self.customer)
        self.authenticate(self.customer)

        response = self.client.delete(self.get_review_detail_url(review.id))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    def test_delete_other_user_review_forbidden(self):
        """Test that users cannot delete others' reviews."""
        other_customer = UserFactory.create_customer()
        review = ReviewFactory.create_review(product=self.product, user=other_customer)
        self.authenticate(self.customer)

        response = self.client.delete(self.get_review_detail_url(review.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ReviewLikeTest(ReviewAPITestCase):
    """Tests for review like/unlike functionality."""

    def test_like_review(self):
        """Test liking a review."""
        review = ReviewFactory.create_review(product=self.product)
        self.authenticate(self.customer)

        response = self.client.post(self.get_review_like_url(review.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["liked"])
        self.assertEqual(response.data["helpful_count"], 1)

    def test_unlike_review(self):
        """Test unliking a previously liked review."""
        review = ReviewFactory.create_review(product=self.product)
        ReviewFactory.create_like(review=review, user=self.customer)
        review.helpful_count = 1
        review.save()

        self.authenticate(self.customer)

        response = self.client.post(self.get_review_like_url(review.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["liked"])
        self.assertEqual(response.data["helpful_count"], 0)

    def test_like_toggle(self):
        """Test that liking twice toggles the state."""
        review = ReviewFactory.create_review(product=self.product)
        self.authenticate(self.customer)

        # First like
        response = self.client.post(self.get_review_like_url(review.id))
        self.assertTrue(response.data["liked"])

        # Second like (unlike)
        response = self.client.post(self.get_review_like_url(review.id))
        self.assertFalse(response.data["liked"])

        # Third like
        response = self.client.post(self.get_review_like_url(review.id))
        self.assertTrue(response.data["liked"])

    def test_like_unauthenticated(self):
        """Test that unauthenticated users cannot like reviews."""
        review = ReviewFactory.create_review(product=self.product)

        response = self.client.post(self.get_review_like_url(review.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewReplyTest(ReviewAPITestCase):
    """Tests for review reply functionality."""

    def test_product_owner_can_reply(self):
        """Test that product owner can reply to reviews."""
        review = ReviewFactory.create_review(product=self.product)
        self.authenticate(self.shopkeeper)  # Product owner

        data = {"comment": "Thank you for your review!"}
        response = self.client.post(self.get_review_reply_url(review.id), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ReviewReply.objects.filter(review=review).exists())

    def test_verified_shopkeeper_can_reply(self):
        """Test that verified shopkeepers can reply to reviews."""
        other_shopkeeper = UserFactory.create_shopkeeper(is_verified=True)
        review = ReviewFactory.create_review(product=self.product)
        self.authenticate(other_shopkeeper)

        data = {"comment": "As a verified seller, I recommend this product!"}
        response = self.client.post(self.get_review_reply_url(review.id), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unverified_shopkeeper_cannot_reply(self):
        """Test that unverified shopkeepers cannot reply to reviews."""
        unverified_shopkeeper = UserFactory.create_shopkeeper(is_verified=False)
        review = ReviewFactory.create_review(product=self.product)
        self.authenticate(unverified_shopkeeper)

        data = {"comment": "Trying to reply without verification!"}
        response = self.client.post(self.get_review_reply_url(review.id), data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_reply(self):
        """Test that regular customers cannot reply to reviews."""
        review = ReviewFactory.create_review(product=self.product)
        self.authenticate(self.customer)

        data = {"comment": "Customers should not be able to reply!"}
        response = self.client.post(self.get_review_reply_url(review.id), data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_reply(self):
        """Test that admin can reply to reviews."""
        admin = UserFactory.create_admin()
        review = ReviewFactory.create_review(product=self.product)
        self.authenticate(admin)

        data = {"comment": "Admin response to customer review."}
        response = self.client.post(self.get_review_reply_url(review.id), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class MyReviewsTest(ReviewAPITestCase):
    """Tests for my reviews endpoint."""

    def test_get_my_reviews(self):
        """Test getting user's own reviews."""
        # Create reviews for current user
        ReviewFactory.create_review(product=self.product, user=self.customer)

        # Create another product and review for same user
        product2 = ProductFactory.create_product(shopkeeper=self.shopkeeper)
        ReviewFactory.create_review(product=product2, user=self.customer)

        # Create review for different user
        other_customer = UserFactory.create_customer()
        product3 = ProductFactory.create_product(shopkeeper=self.shopkeeper)
        ReviewFactory.create_review(product=product3, user=other_customer)

        self.authenticate(self.customer)
        response = self.client.get(self.get_my_reviews_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_get_my_reviews_includes_inactive(self):
        """Test that my reviews includes both active and inactive."""
        ReviewFactory.create_review(
            product=self.product, user=self.customer, is_active=True
        )
        product2 = ProductFactory.create_product(shopkeeper=self.shopkeeper)
        ReviewFactory.create_review(
            product=product2, user=self.customer, is_active=False
        )

        self.authenticate(self.customer)
        response = self.client.get(self.get_my_reviews_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_get_my_reviews_unauthenticated(self):
        """Test that unauthenticated users cannot access my reviews."""
        response = self.client.get(self.get_my_reviews_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
