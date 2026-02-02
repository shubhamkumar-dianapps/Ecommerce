"""
Product Model

Production-ready product model with shopkeeper ownership and comprehensive validation.
"""

from typing import Optional
from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel, SoftDeleteModel
from apps.products.models.category import Category
from apps.products.models.brand import Brand
from apps.products import constants
from apps.products.validators import validate_price, validate_sku


class Product(SoftDeleteModel, TimeStampedModel):
    """
    Product model for e-commerce platform.

    Features:
    - Shopkeeper ownership (products belong to shopkeepers)
    - Multiple product statuses (Draft, Published, etc.)
    - Pricing with discount support
    - SEO-friendly fields
    - Category and brand relationships

    Permissions:
    - Anyone can view published products
    - Only verified shopkeepers can create products
    - Only product owner can edit/delete their products
    """

    class ProductStatus(models.TextChoices):
        """Product status choices"""

        DRAFT = constants.STATUS_DRAFT, "Draft"
        PUBLISHED = constants.STATUS_PUBLISHED, "Published"
        OUT_OF_STOCK = constants.STATUS_OUT_OF_STOCK, "Out of Stock"
        DISCONTINUED = constants.STATUS_DISCONTINUED, "Discontinued"

    # Owner
    shopkeeper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,  # Temporarily nullable for migration
        blank=True,
        help_text="Shopkeeper who owns this product",
    )

    # Basic Information
    name = models.CharField(
        max_length=constants.PRODUCT_NAME_MAX_LENGTH, help_text="Product name"
    )
    slug = models.SlugField(
        max_length=constants.PRODUCT_SLUG_MAX_LENGTH,
        unique=True,
        help_text="URL-friendly product identifier",
    )
    description = models.TextField(help_text="Full product description")
    short_description = models.CharField(
        max_length=constants.PRODUCT_SHORT_DESC_MAX_LENGTH,
        blank=True,
        help_text="Brief description for listings",
    )

    # Relationships
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        help_text="Product category",
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        help_text="Product brand (optional)",
    )

    # Pricing
    price = models.DecimalField(
        max_digits=constants.PRICE_MAX_DIGITS,
        decimal_places=constants.PRICE_DECIMAL_PLACES,
        validators=[validate_price],
        help_text="Current selling price",
    )
    compare_at_price = models.DecimalField(
        max_digits=constants.PRICE_MAX_DIGITS,
        decimal_places=constants.PRICE_DECIMAL_PLACES,
        null=True,
        blank=True,
        help_text="Original price (for showing discounts)",
    )
    cost_price = models.DecimalField(
        max_digits=constants.PRICE_MAX_DIGITS,
        decimal_places=constants.PRICE_DECIMAL_PLACES,
        null=True,
        blank=True,
        help_text="Cost price (for profit calculation)",
    )

    # Product Details
    sku = models.CharField(
        max_length=constants.PRODUCT_SKU_MAX_LENGTH,
        unique=True,
        validators=[validate_sku],
        help_text="Stock Keeping Unit",
    )
    status = models.CharField(
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.DRAFT,
        db_index=True,
        help_text="Product status",
    )
    is_featured = models.BooleanField(
        default=constants.DEFAULT_IS_FEATURED,
        db_index=True,
        help_text="Featured product (shown on homepage)",
    )

    # SEO
    meta_title = models.CharField(
        max_length=constants.PRODUCT_META_TITLE_MAX_LENGTH,
        blank=True,
        help_text="SEO title tag",
    )
    meta_description = models.TextField(blank=True, help_text="SEO meta description")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["sku"]),
            models.Index(fields=["status"]),
            models.Index(fields=["shopkeeper", "status"]),
            models.Index(fields=["category", "status"]),
            models.Index(fields=["is_featured", "status"]),
            models.Index(fields=["price"]),
        ]
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self) -> str:
        """Return product name"""
        return self.name

    @property
    def is_on_sale(self) -> bool:
        """
        Check if product is on sale.

        Returns:
            bool: True if compare_at_price > current price
        """
        return bool(self.compare_at_price and self.compare_at_price > self.price)

    @property
    def discount_percentage(self) -> int:
        """
        Calculate discount percentage.

        Returns:
            int: Discount percentage (0-99)
        """
        if self.is_on_sale and self.compare_at_price:
            return int(
                ((self.compare_at_price - self.price) / self.compare_at_price) * 100
            )
        return 0

    @property
    def profit_margin(self) -> Optional[Decimal]:
        """
        Calculate profit margin.

        Returns:
            Decimal: Profit margin or None if cost_price not set
        """
        if self.cost_price and self.cost_price > 0:
            return self.price - self.cost_price
        return None

    @property
    def profit_percentage(self) -> Optional[int]:
        """
        Calculate profit percentage.

        Returns:
            int: Profit percentage or None if cost_price not set
        """
        if self.cost_price and self.cost_price > 0:
            return int(((self.price - self.cost_price) / self.cost_price) * 100)
        return None

    def publish(self) -> None:
        """Publish the product"""
        self.status = self.ProductStatus.PUBLISHED
        self.save(update_fields=["status"])

    def unpublish(self) -> None:
        """Unpublish the product (set to draft)"""
        self.status = self.ProductStatus.DISCONTINUED
        self.save(update_fields=["status"])

    def mark_out_of_stock(self) -> None:
        """Mark product as out of stock"""
        self.status = self.ProductStatus.OUT_OF_STOCK
        self.save(update_fields=["status"])
