"""
Reviews App Tests - Test Factories

Factory classes for creating test data.
"""

import uuid
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.products.models import Product, Category, Brand
from apps.reviews.models import Review, ReviewLike, ReviewReply

User = get_user_model()


class UserFactory:
    """Factory for creating test users."""

    @staticmethod
    def create_customer(email: str = None, phone: str = None) -> User:
        """Create a customer user with profile."""
        email = email or f"customer_{uuid.uuid4().hex[:8]}@test.com"
        phone = phone or f"+91{uuid.uuid4().int % 10000000000:010d}"

        user = User.objects.create_user(
            email=email,
            phone=phone,
            password="TestPass123!",
            role=User.Role.CUSTOMER,
        )
        # Signal auto-creates CustomerProfile, just update it
        if hasattr(user, "customerprofile"):
            user.customerprofile.full_name = f"Test Customer {uuid.uuid4().hex[:4]}"
            user.customerprofile.save()
        return user

    @staticmethod
    def create_shopkeeper(
        email: str = None, phone: str = None, is_verified: bool = True
    ) -> User:
        """Create a shopkeeper user with profile."""
        email = email or f"shopkeeper_{uuid.uuid4().hex[:8]}@test.com"
        phone = phone or f"+91{uuid.uuid4().int % 10000000000:010d}"

        user = User.objects.create_user(
            email=email,
            phone=phone,
            password="TestPass123!",
            role=User.Role.SHOPKEEPER,
        )
        # Signal auto-creates ShopKeeperProfile, just update it
        if hasattr(user, "shopkeeperprofile"):
            user.shopkeeperprofile.shop_name = f"Test Shop {uuid.uuid4().hex[:4]}"
            user.shopkeeperprofile.gst_number = f"GST{uuid.uuid4().hex[:12].upper()}"
            user.shopkeeperprofile.is_verified = is_verified
            user.shopkeeperprofile.save()
        return user

    @staticmethod
    def create_admin(email: str = None, phone: str = None) -> User:
        """Create an admin user."""
        email = email or f"admin_{uuid.uuid4().hex[:8]}@test.com"
        phone = phone or f"+91{uuid.uuid4().int % 10000000000:010d}"

        user = User.objects.create_user(
            email=email,
            phone=phone,
            password="TestPass123!",
            role=User.Role.ADMIN,
        )
        user.is_staff = True
        user.save()
        return user


class ProductFactory:
    """Factory for creating test products."""

    @staticmethod
    def create_category(name: str = None) -> Category:
        """Create a test category."""
        name = name or f"Category {uuid.uuid4().hex[:6]}"
        return Category.objects.create(
            name=name,
            slug=name.lower().replace(" ", "-"),
            description="Test category description",
        )

    @staticmethod
    def create_brand(name: str = None) -> Brand:
        """Create a test brand."""
        name = name or f"Brand {uuid.uuid4().hex[:6]}"
        return Brand.objects.create(
            name=name,
            slug=name.lower().replace(" ", "-"),
        )

    @staticmethod
    def create_product(
        shopkeeper: User = None,
        category: Category = None,
        name: str = None,
        price: Decimal = None,
    ) -> Product:
        """Create a test product."""
        if shopkeeper is None:
            shopkeeper = UserFactory.create_shopkeeper()
        if category is None:
            category = ProductFactory.create_category()

        name = name or f"Product {uuid.uuid4().hex[:6]}"
        price = price or Decimal("99.99")

        return Product.objects.create(
            shopkeeper=shopkeeper,
            name=name,
            slug=name.lower().replace(" ", "-"),
            description="Test product description",
            category=category,
            price=price,
            sku=f"SKU-{uuid.uuid4().hex[:8].upper()}",
            status=Product.ProductStatus.PUBLISHED,
        )


class ReviewFactory:
    """Factory for creating test reviews."""

    @staticmethod
    def create_review(
        product: Product = None,
        user: User = None,
        rating: Decimal = None,
        title: str = None,
        comment: str = None,
        is_active: bool = True,
    ) -> Review:
        """Create a test review."""
        if product is None:
            product = ProductFactory.create_product()
        if user is None:
            user = UserFactory.create_customer()

        rating = rating or Decimal("4.5")
        title = title or f"Review Title {uuid.uuid4().hex[:6]}"
        comment = comment or "This is a test review comment with sufficient length."

        return Review.objects.create(
            product=product,
            user=user,
            rating=rating,
            title=title,
            comment=comment,
            is_active=is_active,
        )

    @staticmethod
    def create_like(review: Review = None, user: User = None) -> ReviewLike:
        """Create a test review like."""
        if review is None:
            review = ReviewFactory.create_review()
        if user is None:
            user = UserFactory.create_customer()

        return ReviewLike.objects.create(review=review, user=user)

    @staticmethod
    def create_reply(
        review: Review = None,
        user: User = None,
        comment: str = None,
        is_active: bool = True,
    ) -> ReviewReply:
        """Create a test review reply."""
        if review is None:
            review = ReviewFactory.create_review()
        if user is None:
            user = review.product.shopkeeper

        comment = comment or "Thank you for your review!"

        return ReviewReply.objects.create(
            review=review,
            user=user,
            comment=comment,
            is_active=is_active,
        )
