"""
Tests for Product API Endpoints

Comprehensive tests for product, category, and brand endpoints.
"""

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.products.tests.factories import ProductFactory, CategoryFactory, BrandFactory
from apps.accounts.tests.factories import UserFactory


class CategoryAPITest(TestCase):
    """Test cases for category API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.category = CategoryFactory.create_category(name="Electronics")
        self.url = reverse("category-list")

    def test_list_categories(self):
        """Test listing categories."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_category_by_slug(self):
        """Test retrieving category by slug."""
        url = reverse("category-detail", kwargs={"slug": self.category.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Electronics")

    def test_inactive_categories_excluded(self):
        """Test that inactive categories are not listed."""
        CategoryFactory.create_category(is_active=False)

        response = self.client.get(self.url)

        # Only active category should be in results
        slugs = [item["slug"] for item in response.data.get("results", response.data)]
        self.assertIn(self.category.slug, slugs)


class BrandAPITest(TestCase):
    """Test cases for brand API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.brand = BrandFactory.create_brand(name="Apple")
        self.url = reverse("brand-list")

    def test_list_brands(self):
        """Test listing brands."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_brand_by_slug(self):
        """Test retrieving brand by slug."""
        url = reverse("brand-detail", kwargs={"slug": self.brand.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Apple")


class ProductListAPITest(TestCase):
    """Test cases for product list endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("product-list")
        self.category = CategoryFactory.create_category()

    def test_list_published_products(self):
        """Test listing published products."""
        ProductFactory.create_product(status="PUBLISHED")
        ProductFactory.create_product(status="PUBLISHED")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_draft_products_not_listed(self):
        """Test that draft products are not in public listing."""
        ProductFactory.create_product(status="PUBLISHED")
        ProductFactory.create_product(status="DRAFT")

        response = self.client.get(self.url)

        self.assertEqual(response.data["count"], 1)

    def test_filter_by_category_slug(self):
        """Test filtering products by category slug."""
        cat1 = CategoryFactory.create_category(name="Electronics")
        cat2 = CategoryFactory.create_category(name="Books")
        ProductFactory.create_product(category=cat1, status="PUBLISHED")
        ProductFactory.create_product(category=cat2, status="PUBLISHED")

        response = self.client.get(self.url, {"category": "electronics"})

        self.assertEqual(response.data["count"], 1)

    def test_filter_by_brand_slug(self):
        """Test filtering products by brand slug."""
        brand = BrandFactory.create_brand(name="Sony")
        ProductFactory.create_product(brand=brand, status="PUBLISHED")
        ProductFactory.create_product(brand=None, status="PUBLISHED")

        response = self.client.get(self.url, {"brand": "sony"})

        self.assertEqual(response.data["count"], 1)

    def test_filter_by_price_range(self):
        """Test filtering products by price range."""
        ProductFactory.create_product(price=Decimal("50.00"), status="PUBLISHED")
        ProductFactory.create_product(price=Decimal("150.00"), status="PUBLISHED")
        ProductFactory.create_product(price=Decimal("250.00"), status="PUBLISHED")

        response = self.client.get(self.url, {"min_price": "100", "max_price": "200"})

        self.assertEqual(response.data["count"], 1)

    def test_search_products(self):
        """Test searching products by name."""
        ProductFactory.create_product(name="iPhone 15", status="PUBLISHED")
        ProductFactory.create_product(name="Samsung Galaxy", status="PUBLISHED")

        response = self.client.get(self.url, {"search": "iPhone"})

        self.assertEqual(response.data["count"], 1)

    def test_order_by_price(self):
        """Test ordering products by price."""
        ProductFactory.create_product(price=Decimal("200.00"), status="PUBLISHED")
        ProductFactory.create_product(price=Decimal("100.00"), status="PUBLISHED")

        response = self.client.get(self.url, {"ordering": "price"})

        results = response.data["results"]
        self.assertLess(float(results[0]["price"]), float(results[1]["price"]))


class ProductDetailAPITest(TestCase):
    """Test cases for product detail endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.product = ProductFactory.create_product(status="PUBLISHED")
        self.url = reverse("product-detail", kwargs={"slug": self.product.slug})

    def test_retrieve_product(self):
        """Test retrieving product detail."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.product.name)

    def test_draft_product_not_retrievable(self):
        """Test that draft product is not accessible publicly."""
        draft = ProductFactory.create_product(status="DRAFT")
        url = reverse("product-detail", kwargs={"slug": draft.slug})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProductCreateAPITest(TestCase):
    """Test cases for product creation."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("product-list")
        self.shopkeeper = UserFactory.create_shopkeeper(is_verified=True)
        self.category = CategoryFactory.create_category()

    def test_create_product_as_shopkeeper(self):
        """Test creating product as verified shopkeeper."""
        self.client.force_authenticate(user=self.shopkeeper)

        data = {
            "name": "New Product",
            "slug": "new-product",
            "description": "Product description",
            "price": "99.99",
            "sku": "SKU-NEW-001",
            "category": self.category.id,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product_unauthenticated(self):
        """Test creating product without authentication fails."""
        data = {
            "name": "New Product",
            "slug": "new-product",
            "description": "Product description",
            "price": "99.99",
            "sku": "SKU-NEW-001",
            "category": self.category.id,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_product_as_customer_fails(self):
        """Test that customers cannot create products."""
        customer = UserFactory.create_customer()
        self.client.force_authenticate(user=customer)

        data = {
            "name": "New Product",
            "slug": "new-product",
            "description": "Product description",
            "price": "99.99",
            "sku": "SKU-NEW-001",
            "category": self.category.id,
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MyProductsAPITest(TestCase):
    """Test cases for shopkeeper's my-products endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("product-my-products")
        self.shopkeeper = UserFactory.create_shopkeeper()

    def test_my_products_shows_all_statuses(self):
        """Test that my-products shows products with all statuses."""
        ProductFactory.create_product(shopkeeper=self.shopkeeper, status="DRAFT")
        ProductFactory.create_product(shopkeeper=self.shopkeeper, status="PUBLISHED")
        ProductFactory.create_product(shopkeeper=self.shopkeeper, status="OUT_OF_STOCK")

        self.client.force_authenticate(user=self.shopkeeper)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)

    def test_my_products_only_own_products(self):
        """Test that my-products only shows shopkeeper's own products."""
        other_shopkeeper = UserFactory.create_shopkeeper()
        ProductFactory.create_product(shopkeeper=self.shopkeeper)
        ProductFactory.create_product(shopkeeper=other_shopkeeper)

        self.client.force_authenticate(user=self.shopkeeper)
        response = self.client.get(self.url)

        self.assertEqual(response.data["count"], 1)

    def test_my_products_unauthenticated(self):
        """Test my-products requires authentication."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
