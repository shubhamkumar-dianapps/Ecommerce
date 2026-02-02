"""
Tests for Product Models

Comprehensive tests for Product, Category, and Brand models.
"""

from decimal import Decimal
from django.test import TestCase
from apps.products.tests.factories import ProductFactory, CategoryFactory, BrandFactory
from apps.accounts.tests.factories import UserFactory


class CategoryModelTest(TestCase):
    """Test cases for Category model."""

    def test_create_category(self):
        """Test creating a category."""
        category = CategoryFactory.create_category(name="Electronics")

        self.assertEqual(category.name, "Electronics")
        self.assertTrue(category.is_active)

    def test_category_str_representation(self):
        """Test string representation."""
        category = CategoryFactory.create_category(name="Books")
        self.assertEqual(str(category), "Books")

    def test_category_parent_child(self):
        """Test parent-child relationship."""
        parent = CategoryFactory.create_category(name="Electronics")
        child = CategoryFactory.create_category(name="Phones", parent=parent)

        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.children.all())

    def test_inactive_category(self):
        """Test inactive category."""
        category = CategoryFactory.create_category(is_active=False)
        self.assertFalse(category.is_active)


class BrandModelTest(TestCase):
    """Test cases for Brand model."""

    def test_create_brand(self):
        """Test creating a brand."""
        brand = BrandFactory.create_brand(name="Apple")

        self.assertEqual(brand.name, "Apple")
        self.assertTrue(brand.is_active)

    def test_brand_str_representation(self):
        """Test string representation."""
        brand = BrandFactory.create_brand(name="Samsung")
        self.assertEqual(str(brand), "Samsung")


class ProductModelTest(TestCase):
    """Test cases for Product model."""

    def setUp(self):
        self.shopkeeper = UserFactory.create_shopkeeper()
        self.category = CategoryFactory.create_category()

    def test_create_product(self):
        """Test creating a product."""
        product = ProductFactory.create_product(
            shopkeeper=self.shopkeeper,
            name="Test Product",
            category=self.category,
            price=Decimal("99.99"),
        )

        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.price, Decimal("99.99"))
        self.assertEqual(product.shopkeeper, self.shopkeeper)
        self.assertEqual(product.status, "PUBLISHED")

    def test_product_str_representation(self):
        """Test string representation."""
        product = ProductFactory.create_product(name="Amazing Product")
        self.assertEqual(str(product), "Amazing Product")

    def test_product_statuses(self):
        """Test different product statuses."""
        draft = ProductFactory.create_product(status="DRAFT")
        published = ProductFactory.create_product(status="PUBLISHED")
        out_of_stock = ProductFactory.create_product(status="OUT_OF_STOCK")

        self.assertEqual(draft.status, "DRAFT")
        self.assertEqual(published.status, "PUBLISHED")
        self.assertEqual(out_of_stock.status, "OUT_OF_STOCK")


class ProductPricingTest(TestCase):
    """Test cases for product pricing calculations."""

    def test_is_on_sale_true(self):
        """Test is_on_sale when compare_at_price > price."""
        product = ProductFactory.create_product(
            price=Decimal("80.00"), compare_at_price=Decimal("100.00")
        )
        self.assertTrue(product.is_on_sale)

    def test_is_on_sale_false(self):
        """Test is_on_sale when no compare_at_price."""
        product = ProductFactory.create_product(price=Decimal("100.00"))
        self.assertFalse(product.is_on_sale)

    def test_discount_percentage(self):
        """Test discount percentage calculation."""
        product = ProductFactory.create_product(
            price=Decimal("75.00"), compare_at_price=Decimal("100.00")
        )
        self.assertEqual(product.discount_percentage, 25)

    def test_discount_percentage_no_sale(self):
        """Test discount percentage when not on sale."""
        product = ProductFactory.create_product(price=Decimal("100.00"))
        self.assertEqual(product.discount_percentage, 0)

    def test_profit_margin(self):
        """Test profit margin calculation."""
        product = ProductFactory.create_product(
            price=Decimal("100.00"), cost_price=Decimal("60.00")
        )
        self.assertEqual(product.profit_margin, Decimal("40.00"))

    def test_profit_margin_no_cost(self):
        """Test profit margin when no cost_price."""
        product = ProductFactory.create_product(price=Decimal("100.00"))
        self.assertIsNone(product.profit_margin)

    def test_profit_percentage(self):
        """Test profit percentage calculation."""
        product = ProductFactory.create_product(
            price=Decimal("120.00"), cost_price=Decimal("100.00")
        )
        self.assertEqual(product.profit_percentage, 20)


class ProductStatusMethodsTest(TestCase):
    """Test cases for product status methods."""

    def test_publish_method(self):
        """Test publish method."""
        product = ProductFactory.create_product(status="DRAFT")
        product.publish()

        product.refresh_from_db()
        self.assertEqual(product.status, "PUBLISHED")

    def test_unpublish_method(self):
        """Test unpublish method."""
        product = ProductFactory.create_product(status="PUBLISHED")
        product.unpublish()

        product.refresh_from_db()
        self.assertEqual(product.status, "DISCONTINUED")

    def test_mark_out_of_stock_method(self):
        """Test mark_out_of_stock method."""
        product = ProductFactory.create_product(status="PUBLISHED")
        product.mark_out_of_stock()

        product.refresh_from_db()
        self.assertEqual(product.status, "OUT_OF_STOCK")


class ProductRelationshipsTest(TestCase):
    """Test cases for product relationships."""

    def test_product_category_relationship(self):
        """Test product-category relationship."""
        category = CategoryFactory.create_category(name="Electronics")
        product = ProductFactory.create_product(category=category)

        self.assertEqual(product.category, category)
        self.assertIn(product, category.products.all())

    def test_product_brand_relationship(self):
        """Test product-brand relationship."""
        brand = BrandFactory.create_brand(name="Sony")
        product = ProductFactory.create_product(brand=brand)

        self.assertEqual(product.brand, brand)
        self.assertIn(product, brand.products.all())

    def test_product_without_brand(self):
        """Test product can exist without brand."""
        product = ProductFactory.create_product(brand=None)
        self.assertIsNone(product.brand)

    def test_shopkeeper_products(self):
        """Test shopkeeper-products relationship."""
        shopkeeper = UserFactory.create_shopkeeper()
        ProductFactory.create_product(shopkeeper=shopkeeper)
        ProductFactory.create_product(shopkeeper=shopkeeper)

        self.assertEqual(shopkeeper.products.count(), 2)
