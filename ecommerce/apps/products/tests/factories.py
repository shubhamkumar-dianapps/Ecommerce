"""
Test Factories for Products App

Reusable factories for creating test products, categories, and brands.
"""

from decimal import Decimal
from django.utils.text import slugify
from apps.products.models import Product, Category, Brand
from apps.accounts.tests.factories import UserFactory


class CategoryFactory:
    """Factory for creating test categories."""

    _counter = 0

    @classmethod
    def _get_unique_id(cls):
        cls._counter += 1
        return cls._counter

    @classmethod
    def create_category(
        cls, name: str = None, slug: str = None, is_active: bool = True, parent=None
    ) -> Category:
        """Create a test category."""
        unique_id = cls._get_unique_id()
        if name is None:
            name = f"Test Category {unique_id}"
        if slug is None:
            slug = slugify(name)

        return Category.objects.create(
            name=name, slug=slug, is_active=is_active, parent=parent
        )


class BrandFactory:
    """Factory for creating test brands."""

    _counter = 0

    @classmethod
    def _get_unique_id(cls):
        cls._counter += 1
        return cls._counter

    @classmethod
    def create_brand(
        cls, name: str = None, slug: str = None, is_active: bool = True
    ) -> Brand:
        """Create a test brand."""
        unique_id = cls._get_unique_id()
        if name is None:
            name = f"Test Brand {unique_id}"
        if slug is None:
            slug = slugify(name)

        return Brand.objects.create(name=name, slug=slug, is_active=is_active)


class ProductFactory:
    """Factory for creating test products."""

    _counter = 0

    @classmethod
    def _get_unique_id(cls):
        cls._counter += 1
        return cls._counter

    @classmethod
    def create_product(
        cls,
        shopkeeper=None,
        name: str = None,
        slug: str = None,
        price: Decimal = Decimal("100.00"),
        compare_at_price: Decimal = None,
        cost_price: Decimal = None,
        status: str = "PUBLISHED",
        category: Category = None,
        brand: Brand = None,
        is_featured: bool = False,
    ) -> Product:
        """Create a test product."""
        unique_id = cls._get_unique_id()

        if shopkeeper is None:
            shopkeeper = UserFactory.create_shopkeeper()
        if name is None:
            name = f"Test Product {unique_id}"
        if slug is None:
            slug = slugify(name)
        if category is None:
            category = CategoryFactory.create_category()

        return Product.objects.create(
            shopkeeper=shopkeeper,
            name=name,
            slug=slug,
            description=f"Description for {name}",
            short_description=f"Short desc for {name}",
            price=price,
            compare_at_price=compare_at_price,
            cost_price=cost_price,
            sku=f"SKU-{unique_id:06d}",
            status=status,
            category=category,
            brand=brand,
            is_featured=is_featured,
        )
