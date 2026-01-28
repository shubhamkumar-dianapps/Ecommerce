"""
Products Validators

Custom validation functions for products app.
"""

import re
from typing import Any
from decimal import Decimal
from django.core.exceptions import ValidationError
from apps.products import constants


def validate_price(value: Decimal) -> None:
    """
    Validate product price.

    Args:
        value: Price to validate

    Raises:
        ValidationError: If price is invalid
    """
    if value is None:
        raise ValidationError(constants.PRICE_REQUIRED)

    if value <= 0:
        raise ValidationError(constants.INVALID_PRICE)

    if value > constants.MAX_PRICE:
        raise ValidationError(constants.PRICE_TOO_HIGH)


def validate_sku(value: str) -> None:
    """
    Validate SKU format.

    SKU must contain only alphanumeric characters and hyphens.

    Args:
        value: SKU to validate

    Raises:
        ValidationError: If SKU format is invalid

    Examples:
        >>> validate_sku("PROD-12345")  # Valid
        >>> validate_sku("SKU_123")  # Invalid (underscore)
    """
    if not value:
        raise ValidationError(constants.SKU_REQUIRED)

    # Allow alphanumeric and hyphens only
    if not re.match(r"^[A-Z0-9-]+$", value.upper()):
        raise ValidationError(constants.INVALID_SKU_FORMAT)


def validate_slug(value: str) -> None:
    """
    Validate slug format.

    Slug must contain only lowercase letters, numbers, and hyphens.

    Args:
        value: Slug to validate

    Raises:
        ValidationError: If slug format is invalid
    """
    if not value:
        raise ValidationError(constants.SLUG_REQUIRED)

    # Lowercase letters, numbers, and hyphens only
    if not re.match(r"^[a-z0-9-]+$", value):
        raise ValidationError(constants.SLUG_INVALID)


def validate_stock_quantity(value: int) -> None:
    """
    Validate stock quantity.

    Args:
        value: Stock quantity to validate

    Raises:
        ValidationError: If quantity is invalid
    """
    if value < constants.MIN_STOCK_QUANTITY:
        raise ValidationError(constants.STOCK_NEGATIVE)

    if value > constants.MAX_STOCK_QUANTITY:
        raise ValidationError(constants.STOCK_TOO_HIGH)


def validate_discount_percentage(
    selling_price: Decimal, compare_price: Decimal
) -> None:
    """
    Validate discount pricing.

    Compare price must be higher than selling price.

    Args:
        selling_price: Current selling price
        compare_price: Original/compare price

    Raises:
        ValidationError: If discount is invalid
    """
    if compare_price <= selling_price:
        raise ValidationError(constants.COMPARE_PRICE_LOWER)

    discount_pct = ((compare_price - selling_price) / compare_price) * 100

    if (
        discount_pct < constants.MIN_DISCOUNT_PERCENTAGE
        or discount_pct > constants.MAX_DISCOUNT_PERCENTAGE
    ):
        raise ValidationError(constants.DISCOUNT_INVALID)


def validate_image_size(file: Any) -> None:
    """
    Validate uploaded image file size.

    Args:
        file: Uploaded image file

    Raises:
        ValidationError: If file size exceeds limit
    """
    if file.size > constants.MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(constants.IMAGE_TOO_LARGE)


def validate_image_type(file: Any) -> None:
    """
    Validate uploaded image file type.

    Args:
        file: Uploaded image file

    Raises:
        ValidationError: If file type is not allowed
    """
    if file.content_type not in constants.ALLOWED_IMAGE_TYPES:
        raise ValidationError(constants.IMAGE_INVALID_TYPE)
