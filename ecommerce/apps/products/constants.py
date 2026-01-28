"""
Products App Constants

Centralized configuration for all magic numbers, messages, and defaults.
"""

# Field Lengths
PRODUCT_NAME_MAX_LENGTH = 255
PRODUCT_SLUG_MAX_LENGTH = 255
PRODUCT_SHORT_DESC_MAX_LENGTH = 500
PRODUCT_SKU_MAX_LENGTH = 100
PRODUCT_META_TITLE_MAX_LENGTH = 255

CATEGORY_NAME_MAX_LENGTH = 255
CATEGORY_SLUG_MAX_LENGTH = 255

BRAND_NAME_MAX_LENGTH = 255
BRAND_SLUG_MAX_LENGTH = 255

IMAGE_ALT_TEXT_MAX_LENGTH = 255

# Price Configuration
PRICE_MAX_DIGITS = 10
PRICE_DECIMAL_PLACES = 2
MIN_PRICE = 0.01
MAX_PRICE = 99999999.99

# Stock Configuration
MIN_STOCK_QUANTITY = 0
MAX_STOCK_QUANTITY = 999999
DEFAULT_LOW_STOCK_THRESHOLD = 10

# Image Configuration
MAX_IMAGES_PER_PRODUCT = 10
MAX_IMAGE_SIZE_MB = 5
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"]

# Pagination
PRODUCT_PAGE_SIZE = 12
PRODUCT_MAX_PAGE_SIZE = 50
CATEGORY_PAGE_SIZE = 20
CATEGORY_MAX_PAGE_SIZE = 100
BRAND_PAGE_SIZE = 20
BRAND_MAX_PAGE_SIZE = 100

# Product Status
STATUS_DRAFT = "DRAFT"
STATUS_PUBLISHED = "PUBLISHED"
STATUS_OUT_OF_STOCK = "OUT_OF_STOCK"
STATUS_DISCONTINUED = "DISCONTINUED"

# Discount Limits
MIN_DISCOUNT_PERCENTAGE = 0
MAX_DISCOUNT_PERCENTAGE = 99

# Success Messages
PRODUCT_CREATED_SUCCESS = "Product created successfully"
PRODUCT_UPDATED_SUCCESS = "Product updated successfully"
PRODUCT_DELETED_SUCCESS = "Product deleted successfully"
PRODUCT_PUBLISHED_SUCCESS = "Product published successfully"
PRODUCT_UNPUBLISHED_SUCCESS = "Product unpublished successfully"

CATEGORY_CREATED_SUCCESS = "Category created successfully"
BRAND_CREATED_SUCCESS = "Brand created successfully"

IMAGE_UPLOADED_SUCCESS = "Image uploaded successfully"
IMAGE_DELETED_SUCCESS = "Image deleted successfully"

STOCK_UPDATED_SUCCESS = "Stock updated successfully"
STOCK_RESERVED_SUCCESS = "Stock reserved successfully"
STOCK_RELEASED_SUCCESS = "Stock released successfully"

# Error Messages
PRODUCT_NOT_FOUND = "Product not found"
CATEGORY_NOT_FOUND = "Category not found"
BRAND_NOT_FOUND = "Brand not found"

INVALID_PRICE = "Price must be a positive number"
PRICE_TOO_HIGH = f"Price cannot exceed {MAX_PRICE}"
PRICE_REQUIRED = "Price is required"

INVALID_SKU_FORMAT = "SKU must contain only alphanumeric characters and hyphens"
SKU_REQUIRED = "SKU is required"
SKU_ALREADY_EXISTS = "Product with this SKU already exists"

SLUG_REQUIRED = "Slug is required"
SLUG_INVALID = "Slug can only contain lowercase letters, numbers, and hyphens"

STOCK_NEGATIVE = "Stock quantity cannot be negative"
STOCK_TOO_HIGH = f"Stock quantity cannot exceed {MAX_STOCK_QUANTITY}"
INSUFFICIENT_STOCK = "Insufficient stock available"

IMAGE_TOO_LARGE = f"Image size cannot exceed {MAX_IMAGE_SIZE_MB}MB"
IMAGE_INVALID_TYPE = f"Image must be one of: {', '.join(ALLOWED_IMAGE_TYPES)}"
TOO_MANY_IMAGES = f"Cannot upload more than {MAX_IMAGES_PER_PRODUCT} images per product"

NOT_SHOPKEEPER = "Only verified shopkeepers can create/edit products"
NOT_PRODUCT_OWNER = "You can only edit your own products"
SHOPKEEPER_NOT_VERIFIED = "Your shopkeeper account is not yet verified"

DISCOUNT_INVALID = "Discount must be between 0 and 99%"
COMPARE_PRICE_LOWER = "Compare at price must be higher than selling price"

# Filter Options
PRICE_RANGE_MIN = "price_min"
PRICE_RANGE_MAX = "price_max"
IN_STOCK_FILTER = "in_stock"
ON_SALE_FILTER = "on_sale"

# Default Values
DEFAULT_COUNTRY = "India"
DEFAULT_CURRENCY = "INR"
DEFAULT_DISPLAY_ORDER = 0
DEFAULT_IS_ACTIVE = True
DEFAULT_IS_FEATURED = False
DEFAULT_IS_PRIMARY = False
