# Product App - In-Depth Technical Documentation

> **Last Updated**: February 2026  
> **Author**: AI Pair Programmer  
> **Status**: Production Reference  

This document provides an exhaustive, engineer-level breakdown of the **Product App**. It covers the architectural philosophy, technical implementation of inventory management, and high-performance serialization strategies.

---

## 1. Philosophy & Design Decisions

### 1.1 The "Product-Inventory Split" Pattern
**Problem**: In high-traffic e-commerce, stock levels change hundreds of times per minute (reservations, cancellations, sales). Most fields in a Product (name, description, category) are static and can be cached.
**Solution**: We decoupled `Inventory` into its own model.
- **Why?**: Updating `inventory.quantity` doesn't modify the `Product` model's `updated_at` timestamp. This prevents cache invalidation of the entire product catalog every time a single item is sold.
- **Why?**: It allows us to apply a "Pessimistic Locking" strategy (`select_for_update`) ONLY on the inventory row, keeping the Product row free for concurrent read access.

### 1.2 Non-Sequential Identifiers (Slugs & SKU)
**Problem**: Using sequential IDs (`/products/1/`) allows competitors to scrape your catalog size and lets malicious users guess resource locations.
**Solution**: 
- **Slugs**: Used for public URLs (`/products/organic-green-tea/`). They are SEO-friendly and non-guessable.
- **SKU (Stock Keeping Unit)**: Used for internal logic and inventory tracking. It follows a strict format (`[A-Z0-9-]+`) to ensure compatibility with warehouse systems.

### 1.3 Soft Deletion & Data Integrity
Products wrap around `SoftDeleteModel`. 
- **Reason**: If a product is sold, it's linked to an `OrderItem`. Deleting the product from the DB would break financial reports and order history. 
- **Behavior**: `is_deleted=True` makes the product invisible to the store but keeps the row intact for database integrity and audit purposes.

---

## 2. Models Deep Dive

### 2.1 The Product Model (`models/product.py`)
This is the central entity. It inherits from `SoftDeleteModel` and `TimeStampedModel`.

| Field | Purpose | Validation / Constraint |
|-------|---------|-------------------------|
| `shopkeeper` | Ownership | `ForeignKey` to User. Links product to its seller. |
| `slug` | Public ID | `unique=True`. Indexed for fast lookups in URLs. |
| `sku` | Inventory ID | `unique=True`. Validated via `validate_sku`. |
| `price` | Selling Price | `Decimal(10,2)`. Validated to be positive. |
| `compare_at_price` | Original Price | Used for "Discount" display logic. |
| `cost_price` | Hidden Cost | Internal only. Used to calculate profit margins. |
| `status` | Visibility | `DRAFT`, `PUBLISHED`, `OUT_OF_STOCK`, `DISCONTINUED`. |

**Computed Properties (Business Logic)**:
- `is_on_sale`: Boolean logic determining if a discount badge should be shown.
- `discount_percentage`: Integer math for the frontend (e.g., "30% OFF").
- `profit_margin`: Calculated as `price - cost_price` for administrative dashboards.

### 2.2 The Inventory Model (`models/inventory.py`)
The "engine" for transaction safety.

- **`quantity`**: Total physical stock in the warehouse.
- **`reserved`**: Stock currently "locked" in users' carts (checkout sessions).
- **`available` (Property)**: `quantity - reserved`. This is what the frontend shows as "In Stock".

### 2.3 Category & Brand (`models/category.py`, `models/brand.py`)
- **Self-referential Category**: Uses a `parent` ForeignKey to itself. This supports multi-level hierarchies (e.g., *Electronics > Computers > Laptops*).
- **Optimization**: `get_all_children()` is a recursive helper that allows filtering products within a parent category (including all its sub-categories).

---

## 3. Inventory Atomicity & Race Conditions

This is the most technically critical part of the app. We must prevent **Overselling** (selling 10 items when only 5 are in stock).

### 3.1 The "Reserve" Logic (`inventory.reserve()`)
When a user adds an item to their cart or starts checkout:
1. We start a **Database Transaction** (`@transaction.atomic`).
2. We call `select_for_update()` on the `Inventory` row. This "locks" the row so no other user can change the stock until we are done.
3. We check if `available >= requested_qty`.
4. If valid, we increment `reserved` and save.

```python
# Example of the atomic lock
locked_inventory = Inventory.objects.select_for_update().get(pk=self.pk)
if locked_inventory.available >= quantity:
    locked_inventory.reserved += quantity
    locked_inventory.save()
```

### 3.2 Confirmation vs. Release
- **Confirmation**: If payment succeeds, we subtract the amount from both `quantity` and `reserved`.
- **Release**: If the user abandons their cart, we subtract from `reserved`, making that stock "available" for others again.

---

## 4. Multi-Tier Serialization Strategy

To ensure high performance (especially on the homepage), we use different serializers based on the view's needs.

### 4.1 `ProductListSerializer` (Optimization: Prefetching)
**Usage**: Product listing pages, Search results.
- **Depth**: Shallow. 
- **Optimization**: We use `SerializerMethodField` for `primary_image`. To avoid "N+1 queries" (100 products = 100 extra queries for images), the ViewSet uses `to_attr="primary_images"` prefetching. The serializer simply reads the pre-fetched attribute from memory.

### 4.2 `ProductDetailSerializer`
**Usage**: Product detail page.
- **Depth**: Deep.
- **Content**: Includes full JSON objects for `Category`, `Brand`, and the entire `Inventory` status. 

### 4.3 `ProductCreateUpdateSerializer`
**Usage**: Shopkeeper dashboard.
- **Strictness**: Highly validated.
- **Content**: Includes `cost_price` (which is never exposed to customers).

---

## 5. Security & Access Control

Permissions are defined in `permissions.py` and applied in the ViewSet.

| Action | Permission | Logic |
|--------|------------|-------|
| `List` | `AllowAny` | Only shows `status=PUBLISHED` and `is_deleted=False`. |
| `Retrieve`| `AllowAny` | Fetch by `Slug`. |
| `Create` | `IsVerifiedShopkeeper` | Checks `User.Role == SHOPKEEPER` AND `Profile.is_verified`. |
| `Update` | `IsProductOwner` | Checks `product.shopkeeper == request.user`. |
| `Delete` | `IsProductOwner` | Performs a "Soft Delete" (sets `is_deleted=True`). |

---

## 6. Functional Architecture & Flows

### 6.1 Product Creation Flow
1. Shopkeeper sends `POST /api/products/`.
2. `ProductCreateUpdateSerializer` validates `SKU` and `Slug` uniqueness.
3. `perform_create()` automatically assigns the `request.user` to the `shopkeeper` field.
4. An `Inventory` row is automatically created (via Django Signals or manual logic) to start at 0 stock.

### 6.2 Filtering Logic (`filters.py`)
We use `django-filter` to provide powerful storefront capabilities:
- `?category=electronics`: Filters by category slug (not ID).
- `?min_price=100&max_price=500`: Range-based pricing.
- `?is_featured=true`: Highlighted products for the homepage.
- `search=iphone`: Full-text search across `name`, `description`, and `SKU`.

---

## Summary

The Product app is built to sustain a high-volume marketplace. Key Takeaways:
1.  **Safety First**: Pessimistic locking in `Inventory` prevents overselling.
2.  **Performance Built-in**: Annotated queries and primary image prefetching ensure the storefront loads in milliseconds.
3.  **SEO Ready**: Automatic slug validation and meta-fields support modern digital marketing requirements.
4.  **Ownership Model**: Strict object-level permissions ensure shopkeepers can only manage their own inventory.
