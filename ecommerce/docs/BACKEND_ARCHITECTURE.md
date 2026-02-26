# E-Commerce Backend Architecture Documentation

**Project**: Production-Grade E-Commerce Backend  
**Framework**: Django 5.x + Django Rest Framework  
**Author**: Development Team  
**Last Updated**: February 2026

---

## Table of Contents

1. [High-Level System Overview](#1-high-level-system-overview)
2. [Project Folder Structure](#2-project-folder-structure)
3. [Settings and Configuration](#3-settings-and-configuration)
4. [User and Authentication System](#4-user-and-authentication-system)
5. [Models Design](#5-models-design)
6. [Serializers Strategy](#6-serializers-strategy)
7. [Views, ViewSets and Mixins](#7-views-viewsets-and-mixins)
8. [Pagination, Filtering and Searching](#8-pagination-filtering-and-searching)
9. [SQL and Performance Optimization](#9-sql-and-performance-optimization)
10. [Transactions and Data Consistency](#10-transactions-and-data-consistency)
11. [Middleware and Request Lifecycle](#11-middleware-and-request-lifecycle)
12. [Permissions and Security](#12-permissions-and-security)
13. [Error Handling and Validation](#13-error-handling-and-validation)
14. [Payment Flow](#14-payment-flow)
15. [Key Concepts Learned](#15-key-concepts-learned)
16. [Future Improvements](#16-future-improvements)

---

## 1. High-Level System Overview

### What Problem This Backend Solves

This backend powers a multi-vendor e-commerce platform where:

- **Shopkeepers** can register, list products, manage inventory, and handle orders
- **Customers** can browse products, add to cart, checkout, and leave reviews
- **Admins** can manage users, verify shopkeepers, and oversee the platform

### Why Django + DRF Was Chosen

- **Django ORM**: Handles complex data relationships (products, orders, users) with automatic query optimization
- **Django Admin**: Built-in admin panel for quick management without frontend development
- **DRF**: Industry-standard for building RESTful APIs with built-in serialization, validation, and authentication
- **Mature Ecosystem**: JWT authentication, filtering, pagination libraries are battle-tested
- **Monolithic Start**: Easier to develop, deploy, and debug than microservices for an MVP

### How This Backend Scales

- **Horizontal Scaling**: Stateless JWT authentication allows multiple server instances behind a load balancer
- **Database Optimization**: Indexes on frequently queried fields, prefetch_related for reducing queries
- **Cursor Pagination**: For large datasets (products, reviews), prevents offset-based performance degradation
- **Service Layer**: Business logic is decoupled from views, making it easy to move to async workers later

### Overall Request to Response Flow

```
Client Request
    |
    v
[Middleware Stack] (Security, Session, CORS, Auth)
    |
    v
[URL Router] (urls.py)
    |
    v
[Permission Classes] (Role-based access check)
    |
    v
[ViewSet/APIView] (Request handling)
    |
    v
[Serializer] (Validation + Transformation)
    |
    v
[Service Layer] (Business logic)
    |
    v
[Model/ORM] (Database operations)
    |
    v
[Serializer] (Response formatting)
    |
    v
Client Response (JSON)
```

---

## 2. Project Folder Structure

```
ecommerce/
├── config/                      # Project configuration
│   ├── settings/
│   │   ├── base.py              # Shared settings
│   │   ├── dev.py               # Development overrides
│   │   ├── prod.py              # Production overrides
│   │   └── test.py              # Test overrides
│   ├── urls.py                  # Root URL configuration
│   ├── exception_handlers.py    # Custom error responses
│   └── views.py                 # Health check, root views
│
├── apps/
│   ├── accounts/                # User, authentication, profiles
│   ├── addresses/               # Customer shipping/billing addresses
│   ├── products/                # Products, categories, brands, inventory
│   ├── cart/                    # Shopping cart
│   ├── orders/                  # Orders, checkout, order items
│   ├── reviews/                 # Product reviews and replies
│   └── common/                  # Shared utilities, base models
│
├── docs/                        # Documentation
├── media/                       # User-uploaded files
├── postman/                     # API collection for testing
└── manage.py
```

### App Responsibilities

| App | Responsibility | Interacts With |
|-----|----------------|----------------|
| **accounts** | User model, authentication, profiles, sessions | All apps (User FK) |
| **addresses** | Shipping/billing addresses, validation | accounts, orders |
| **products** | Product catalog, inventory, categories | accounts (shopkeeper), cart, orders, reviews |
| **cart** | Shopping cart, cart items | accounts (customer), products |
| **orders** | Order creation, checkout, order history | accounts, products, addresses, cart |
| **reviews** | Product reviews, likes, replies | accounts, products |
| **common** | Base models (TimeStamped, SoftDelete), constants | All apps inherit from it |

### Why This Structure

- **Single Responsibility**: Each app handles one domain
- **Loose Coupling**: Apps communicate via ForeignKeys, not direct imports where possible
- **Testability**: Each app can be tested in isolation
- **Django Convention**: Standard Django app structure for familiarity

---

## 3. Settings and Configuration

### Why Settings Are Split

```python
# base.py - Shared across all environments
# dev.py  - DEBUG=True, console email, Silk profiler
# prod.py - DEBUG=False, real email, security headers
# test.py - Fast password hasher, in-memory database
```

**Problem Without Split**: A single settings.py leads to:
- Accidental DEBUG=True in production
- Environment-specific code with if/else statements
- Hard to override for testing

**Solution**: Import chain (prod.py imports base.py and overrides)

### Installed Apps Reasoning

```python
INSTALLED_APPS = [
    # Django built-ins (required)
    "django.contrib.admin",        # Admin interface
    "django.contrib.auth",         # Authentication framework
    "django.contrib.contenttypes", # Content type system (required by auth)
    "django.contrib.sessions",     # Session management for admin
    "django.contrib.messages",     # Flash messages
    "django.contrib.staticfiles",  # Static file serving

    # Third-party (order matters for some)
    "rest_framework",              # DRF core
    "rest_framework_simplejwt",    # JWT authentication
    "corsheaders",                 # CORS handling
    "django_filters",              # Query filtering
    "phonenumber_field",           # Phone validation

    # Local apps (order matters for migrations)
    "apps.accounts",               # First (User model)
    "apps.addresses",
    "apps.products",
    "apps.cart",
    "apps.orders",
    "apps.reviews",
]
```

### Middleware Ordering (CRITICAL)

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",      # 1. Security headers first
    "django.contrib.sessions.middleware.SessionMiddleware", # 2. Sessions (admin needs this)
    "corsheaders.middleware.CorsMiddleware",              # 3. CORS before CommonMiddleware
    "django.middleware.common.CommonMiddleware",          # 4. URL normalization
    "django.middleware.csrf.CsrfViewMiddleware",          # 5. CSRF protection
    "django.contrib.auth.middleware.AuthenticationMiddleware", # 6. User authentication
    "django.contrib.messages.middleware.MessageMiddleware", # 7. Flash messages
    "django.middleware.clickjacking.XFrameOptionsMiddleware", # 8. Clickjacking protection
]
```

**Why Order Matters**:
- CORS must run before CommonMiddleware, or preflight requests fail
- Authentication must run before any permission checks
- Security headers must be added first, before response is sent

### What Happens If Removed

| Setting | If Removed |
|---------|-----------|
| `SECRET_KEY` | Cryptographic operations fail, sessions break |
| `ALLOWED_HOSTS` (in prod) | Every request returns 400 Bad Request |
| `AUTH_USER_MODEL` | Django uses default User model, breaking all FKs |
| `EXCEPTION_HANDLER` | Errors return HTML instead of JSON |
| CORS middleware | Frontend cannot make API calls (blocked by browser) |

### Environment Variable Usage

```python
# All secrets come from environment
SECRET_KEY = env("SECRET_KEY")
DATABASE_URL = env("DATABASE_URL")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

# Defaults provided for development
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
```

**Why**: Secrets never in version control. Same codebase works in dev/prod.

---

## 4. User and Authentication System

### Why Custom User Model Was Used

Django's default User model has:
- Username as primary identifier (we use email)
- No phone number field
- No role system
- Integer primary key (we use UUID)

**Our Custom User Model**:

```python
class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    class Role(models.TextChoices):
        ADMIN = "ADMIN"
        SHOPKEEPER = "SHOPKEEPER"
        CUSTOMER = "CUSTOMER"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(unique=True, validators=[validate_phone_number])
    role = models.CharField(choices=Role.choices)
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"  # Login with email
    REQUIRED_FIELDS = ["phone", "role"]
```

### Role Handling

| Role | Can Do |
|------|--------|
| **ADMIN** | Manage users, verify shopkeepers, view all data |
| **SHOPKEEPER** | Create products, manage inventory, view own orders |
| **CUSTOMER** | Browse, cart, checkout, review purchased products |

**Why Roles in User Model**:
- Single table query to check permissions
- No additional join needed
- Simple string comparison in permission classes

### Authentication Flow (JWT)

1. **Login**: POST `/api/v1/accounts/login/` with email + password
2. **Validate**: Check password, check is_active
3. **Generate**: Create access token (60 min) + refresh token (1 day)
4. **Session**: Create UserSession record with IP, user agent
5. **Response**: Return tokens + user info

```
POST /login/ {email, password}
    |
    v
LoginSerializer.validate()
    - Check user exists
    - Check is_active
    - Check password (bcrypt)
    |
    v
AuthService.create_session()
    - Lock existing sessions (select_for_update)
    - Check max sessions limit
    - Invalidate oldest if limit exceeded
    - Create new session record
    |
    v
Return {access, refresh, session_id, user}
```

### Token Lifecycle

| Token | Lifetime | Purpose |
|-------|----------|---------|
| Access Token | 60 minutes (configurable) | Authenticate API requests |
| Refresh Token | 1 day (configurable) | Get new access token without re-login |

**Why Short Access Token**:
- Limits damage if token is stolen
- Forces periodic refresh (we can check if user is still active)

### Password Validation Strategy

```python
AUTH_PASSWORD_VALIDATORS = [
    UserAttributeSimilarityValidator,  # Not similar to email
    MinimumLengthValidator,            # At least 8 characters
    CommonPasswordValidator,           # Not "password123"
    NumericPasswordValidator,          # Not all numbers
    EnhancedPasswordValidator,         # Custom: uppercase, lowercase, digit, special
]
```

**Why Multiple Validators**: Defense in depth. Each catches different weak passwords.

### Registration Flow

```
POST /register/customer/ {email, phone, password, password_confirm, full_name}
    |
    v
CustomerRegistrationSerializer
    - Validate email unique
    - Validate phone format
    - Validate password strength
    - Check password_confirm matches
    |
    v
RegistrationMixin.perform_create()
    - serializer.save() -> Create User + CustomerProfile
    - EmailService.send_verification_email()
    - AuditService.log_account_created()
    |
    v
Return {message, user: {id, email, role, email_verified}}
```

---

## 5. Models Design

### Accounts App Models

#### User Model

```python
class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    id = models.UUIDField(primary_key=True)      # No sequential IDs exposed
    email = models.EmailField(unique=True, db_index=True)  # Fast lookups
    phone = models.CharField(unique=True, db_index=True)   # Fast lookups
    role = models.CharField(choices=Role.choices)
    email_verified = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)  # Soft delete support
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
```

**Why UUID Primary Key**:
- Security: Cannot guess user IDs (123, 124, etc.)
- Distributed systems: Can generate IDs without database

**Why db_index on email and phone**:
- Login queries filter by email
- Phone lookup for OTP (future feature)

#### CustomerProfile / ShopkeeperProfile

Separate profile tables instead of putting all fields in User:

```python
class CustomerProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField()
    # Customer-specific fields

class ShopkeeperProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField()
    gst_number = models.CharField()
    is_verified = models.BooleanField(default=False)
    # Shopkeeper-specific fields
```

**Why Separate Tables**:
- User table stays lean (faster queries)
- Role-specific fields don't clutter other roles
- Can add fields without affecting unrelated users

#### UserSession

```python
class UserSession(TimeStampedModel):
    user = models.ForeignKey(User)
    session_key = models.CharField(unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField()
```

**Why Track Sessions**:
- Limit concurrent logins (MAX_SESSIONS = 3)
- Show "active sessions" to user
- Allow "logout all devices"

### Products App Models

#### Product Model

```python
class Product(SoftDeleteModel, TimeStampedModel):
    shopkeeper = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(null=True)  # Original price
    cost_price = models.DecimalField(null=True)        # For profit calculation

    sku = models.CharField(unique=True)
    status = models.CharField(choices=ProductStatus.choices)
    is_featured = models.BooleanField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["sku"]),
            models.Index(fields=["status"]),
            models.Index(fields=["shopkeeper", "status"]),
            models.Index(fields=["category", "status"]),
            models.Index(fields=["is_featured", "status"]),
            models.Index(fields=["price"]),
        ]
```

**Why on_delete Choices**:
- `CASCADE` on shopkeeper: If shopkeeper deleted, their products go too
- `PROTECT` on category: Cannot delete category if products exist
- `SET_NULL` on brand: Products remain if brand deleted

**Why Multiple Indexes**:
```python
# Common queries need fast lookups:
Product.objects.filter(status="PUBLISHED")                    # Uses status index
Product.objects.filter(category_id=5, status="PUBLISHED")     # Uses composite index
Product.objects.filter(is_featured=True, status="PUBLISHED")  # Uses composite index
Product.objects.filter(price__gte=100, price__lte=500)        # Uses price index
```

#### Inventory Model

```python
class Inventory(TimeStampedModel):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    reserved = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)

    @property
    def available(self):
        return self.quantity - self.reserved

    def reserve(self, quantity):
        if quantity > self.available:
            return False
        self.reserved += quantity
        self.save()
        return True
```

**Why Separate Inventory Model**:
- Inventory changes frequently (reservations, restocks)
- Product table can be cached (rarely changes)
- Clear separation of concerns

**Why Reserved Field**:
- Prevents overselling
- User adds to cart -> reserve
- Order confirmed -> subtract from quantity, clear reserved
- Order cancelled -> release reserved

### Orders App Models

#### Order Model

```python
class Order(TimeStampedModel):
    order_number = models.CharField(unique=True, editable=False)  # ORD-ABC123
    user = models.ForeignKey(User, on_delete=models.PROTECT)

    # Snapshot at order time
    shipping_address = models.ForeignKey(Address, on_delete=models.PROTECT)
    billing_address = models.ForeignKey(Address, on_delete=models.PROTECT, null=True)

    subtotal = models.DecimalField()
    shipping_cost = models.DecimalField()
    tax = models.DecimalField()
    total = models.DecimalField()

    status = models.CharField(choices=OrderStatus.choices)
    payment_status = models.CharField(choices=PaymentStatus.choices)
```

**Why PROTECT on User and Address**:
- Cannot delete user with orders (business records)
- Cannot delete address used in orders (historical accuracy)

**Why Store Totals Instead of Computing**:
- Historical accuracy: Prices may change later
- Performance: No need to recompute on every view
- Audit trail: Exact amounts at order time

#### OrderItem Model

```python
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    # Snapshot at order time
    product_name = models.CharField()
    product_sku = models.CharField()
    unit_price = models.DecimalField()
    quantity = models.PositiveIntegerField()
```

**Why Snapshot Product Details**:
- Product name may change later
- Price may change later
- Product may be deleted (PROTECT prevents, but still good practice)

### Cart App Models

```python
class Cart(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    @property
    def total_items(self):
        # DB aggregation: Single query
        return self.items.aggregate(total=Sum("quantity"))["total"] or 0

    @property
    def subtotal(self):
        # DB aggregation with F expression: Single query
        return self.items.aggregate(
            total=Sum(F("quantity") * F("product__price"))
        )["total"] or 0

class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart)
    product = models.ForeignKey(Product)
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ("cart", "product")  # One entry per product
```

**Why OneToOneField for Cart**:
- Each user has exactly one cart
- Simplifies "get or create" logic

**Why unique_together**:
- Prevents duplicate cart items
- Database enforces constraint

**Why DB Aggregation**:
```python
# Bad: N+1 queries
total = sum(item.quantity * item.product.price for item in cart.items.all())

# Good: Single query
total = cart.items.aggregate(total=Sum(F("quantity") * F("product__price")))["total"]
```

### Common Base Models

```python
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)

    objects = models.Manager()           # All objects
    active_objects = SoftDeleteManager() # Non-deleted only

    def delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    class Meta:
        abstract = True
```

**Why Abstract Base Classes**:
- DRY: Every model gets timestamps without copy-paste
- Consistency: All models have same field names
- Maintainability: Change in one place affects all

---

## 6. Serializers Strategy

### Why Serializers Are Split

```
ProductListSerializer     -> For listing (minimal data)
ProductDetailSerializer   -> For single product view (full data)
ProductCreateSerializer   -> For creating/updating (write fields)
```

**Problem Without Split**:
```python
# Bad: One serializer doing everything
class ProductSerializer:
    user = UserSerializer()  # Nested user for detail
    images = ImageSerializer(many=True)  # All images

# On list view: This fetches user + images for 20 products = slow
```

**Solution**:
```python
class ProductListSerializer:
    # Lightweight, only fields needed for cards
    fields = ["id", "name", "price", "image"]

class ProductDetailSerializer:
    # Full data for single product view
    user = UserSerializer()
    images = ImageSerializer(many=True)
    fields = ["id", "name", "description", "price", "specs", "reviews"...]
```

### When Nested Serializers Are Used

Used when:
- Detail views where related data is needed
- Data is already prefetched
- Client needs the data in one request

```python
class ReviewDetailSerializer:
    user_name = serializers.SerializerMethodField()
    replies = ReviewReplySerializer(many=True)  # Nested
```

### When Nested Serializers Are Avoided

Avoided when:
- List views where minimal data is sufficient
- Related data causes N+1 queries
- Client can fetch related data separately

```python
class ReviewListSerializer:
    user_name = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()  # Just count, not full data
```

### Validation Logic Location

| Validation Type | Location | Why |
|----------------|----------|-----|
| Field format (email, phone) | Model field validators | Enforced at database level |
| Business rules | Serializer.validate() | Before save, can access related data |
| Cross-field validation | Serializer.validate() | Can compare multiple fields |
| Authorization | Permission classes | Before serializer runs |

```python
class ReviewCreateSerializer:
    def validate(self, attrs):
        # Business rule: No duplicate reviews
        if Review.objects.filter(product=attrs["product"], user=self.context["request"].user).exists():
            raise ValidationError("You have already reviewed this product")

        # Business rule: Cannot review own product
        if attrs["product"].shopkeeper == self.context["request"].user:
            raise ValidationError("Cannot review your own product")

        return attrs
```

### Serializer Performance Concerns

**Problem**: SerializerMethodField causes queries
```python
def get_user_name(self, obj):
    return obj.user.customerprofile.full_name  # Extra query per object!
```

**Solution**: Prefetch in queryset
```python
def get_queryset(self):
    return Review.objects.select_related(
        "user__customerprofile"  # Prefetch profile
    )
```

---

## 7. Views, ViewSets and Mixins

### Why ViewSets Were Chosen

**ViewSets provide**:
- Automatic URL routing
- Standard CRUD actions
- Less boilerplate

```python
class ProductViewSet(viewsets.ModelViewSet):
    # Automatically creates:
    # GET    /products/        -> list
    # POST   /products/        -> create
    # GET    /products/{id}/   -> retrieve
    # PUT    /products/{id}/   -> update
    # PATCH  /products/{id}/   -> partial_update
    # DELETE /products/{id}/   -> destroy
```

### Why Mixins Are Used

**Problem**: Repeating same logic in multiple views
```python
# Customer registration view
class CustomerRegisterView:
    def perform_create(serializer):
        user = serializer.save()
        send_verification_email(user)
        log_account_creation(user)

# Shopkeeper registration view (same logic!)
class ShopkeeperRegisterView:
    def perform_create(serializer):
        user = serializer.save()
        send_verification_email(user)
        log_account_creation(user)
```

**Solution**: Extract common logic into mixin
```python
class RegistrationMixin:
    def perform_create(self, serializer):
        user = serializer.save()
        self.send_verification_email(user)
        self.log_account_creation(user)
        return user

class CustomerRegisterView(RegistrationMixin, CreateAPIView):
    pass

class ShopkeeperRegisterView(RegistrationMixin, CreateAPIView):
    def get_success_message(self, user):
        return super().get_success_message(user) + " Admin verification pending."
```

### Custom Mixins in This Project

| Mixin | Purpose |
|-------|---------|
| `EmailVerificationMixin` | Sends verification email after user creation |
| `AuditLoggingMixin` | Logs account creation to audit service |
| `RegistrationMixin` | Combines above + standardized response format |

### How Permissions Are Enforced

```python
class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsShopkeeperOrReadOnly,  # Shopkeepers can write, others can read
        IsProductOwner,          # Only owner can edit/delete their products
    ]
```

**How DRF Processes Permissions**:
1. Request arrives
2. DRF runs `has_permission()` for each permission class
3. If any returns False -> 403 Forbidden
4. For object-level, `has_object_permission()` is also checked

### How QuerySets Are Optimized

```python
def get_queryset(self):
    return (
        Product.objects
        .filter(status="PUBLISHED")
        .select_related("category", "brand")  # FK joins
        .prefetch_related("images")            # Separate query, in-memory join
        .annotate(review_count=Count("reviews"))
    )
```

### Where Business Logic Lives

| Component | Contains |
|-----------|----------|
| Views | HTTP handling, permission checks, serializer orchestration |
| Serializers | Validation, data transformation |
| Services | Business logic, database transactions |
| Models | Data structure, simple computed properties |

**Why Services**:
- Reusable from views, Celery tasks, management commands
- Easier to test (no HTTP context needed)
- Single responsibility

```python
# services/checkout_service.py
class CheckoutService:
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(user, shipping_address_id):
        cart = Cart.objects.get(user=user)
        # Validate cart not empty
        # Validate addresses
        # Reserve inventory
        # Create order
        # Create order items
        # Clear cart
        return order
```

---

## 8. Pagination, Filtering and Searching

### Why Pagination Is Mandatory

**Without Pagination**:
```python
# Bad: Returns 10,000 products in one response
Product.objects.all()  # 10,000 rows
# Problems:
# - Slow query
# - Large JSON response (MBs)
# - Client memory issues
# - Network timeout
```

**With Pagination**:
```python
# Good: Returns 10 products + links to next page
{
    "results": [...10 products...],
    "next": "?cursor=abc123"
}
```

### Custom Pagination Classes

**PageNumberPagination** (for categories, brands):
```python
class CategoryPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
```

**CursorPagination** (for products, reviews):
```python
class ProductPagination(CursorPagination):
    page_size = 12
    ordering = "-created_at"
    cursor_query_param = "cursor"
```

**Why Cursor for Products**:
- No count query (expensive on large tables)
- Consistent results during infinite scroll (new products don't shift pages)
- Better performance (uses indexed ordering column)

### Filtering Strategy

```python
class ProductViewSet:
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "brand", "is_featured", "status"]
    search_fields = ["name", "description", "sku"]
    ordering_fields = ["price", "created_at", "name"]
```

**URL Examples**:
```
/products/?category=1&is_featured=true
/products/?search=laptop
/products/?ordering=-price
```

### Query Optimization Impact

Filtering happens at database level:
```python
# DjangoFilterBackend generates:
SELECT * FROM products WHERE category_id = 1 AND is_featured = true

# NOT Python filtering:
[p for p in Product.objects.all() if p.category_id == 1]  # Bad!
```

---

## 9. SQL and Performance Optimization

### select_related vs prefetch_related

**select_related** (for ForeignKey, OneToOne):
```python
# Without: 1 + N queries
reviews = Review.objects.all()
for r in reviews:
    print(r.user.email)  # Query per review

# With: 1 query (SQL JOIN)
reviews = Review.objects.select_related("user")
for r in reviews:
    print(r.user.email)  # No extra query
```

**prefetch_related** (for ManyToMany, reverse FK):
```python
# Without: 1 + N queries
products = Product.objects.all()
for p in products:
    print(p.images.all())  # Query per product

# With: 2 queries (products, then all related images)
products = Product.objects.prefetch_related("images")
for p in products:
    print(p.images.all())  # Uses prefetched cache
```

### Annotation Usage

```python
# Get products with review count (single query)
products = Product.objects.annotate(
    review_count=Count("reviews"),
    avg_rating=Avg("reviews__rating")
)

# Access computed fields
for p in products:
    print(p.review_count, p.avg_rating)  # No extra queries
```

### Index Usage

Every filter/ordering field should have an index:
```python
class Meta:
    indexes = [
        models.Index(fields=["status"]),              # For filter
        models.Index(fields=["created_at"]),          # For ordering
        models.Index(fields=["shopkeeper", "status"]), # For composite filter
    ]
```

### Query Count Reduction Example

**Before** (cart endpoint: 14 queries):
```python
def list(request):
    cart = Cart.objects.get(user=request.user)
    serializer = CartSerializer(cart)  # Triggers N+1
```

**After** (cart endpoint: 4 queries):
```python
def list(request):
    cart = Cart.objects.prefetch_related(
        Prefetch(
            "items",
            queryset=CartItem.objects.select_related(
                "product",
                "product__category",
                "product__brand",
                "product__inventory",
            )
        )
    ).get(user=request.user)
    serializer = CartSerializer(cart)
```

### When Raw SQL Is Acceptable

Almost never in this project. ORM handles:
- Complex joins (select_related)
- Aggregations (annotate, aggregate)
- Subqueries (Subquery, OuterRef)

Raw SQL only if:
- Database-specific feature needed
- Performance critical and ORM cannot optimize

---

## 10. Transactions and Data Consistency

### Why Atomic Transactions Are Needed

**Problem**: Operations can fail midway
```python
# BAD: No transaction
def checkout():
    order = Order.objects.create(...)      # Success
    reserve_inventory()                     # Fails!
    # Now we have an order with no inventory reserved
```

**Solution**: Atomic transaction
```python
@transaction.atomic
def checkout():
    order = Order.objects.create(...)
    reserve_inventory()  # If this fails, order creation is rolled back
```

### Where Transactions Are Used

1. **Checkout**: Order + OrderItems + Inventory reservation
2. **Add to Cart**: Check inventory + Update cart item
3. **Session Management**: Check session limit + Create new session
4. **Like Toggle**: Check existing + Update count

### What Problems They Prevent

| Scenario | Without Transaction | With Transaction |
|----------|---------------------|------------------|
| Checkout fails at inventory | Order created, no items | Everything rolled back |
| Two users buy last item | Both succeed (oversold) | One succeeds, one fails |
| Server crash mid-operation | Partial data | No partial data |

### Race Condition Prevention

```python
@transaction.atomic
def add_item(user, product_id, quantity):
    # Lock product row to prevent concurrent modifications
    product = Product.objects.select_for_update().get(id=product_id)

    if product.inventory.available < quantity:
        raise ValueError("Insufficient stock")

    # Safe to proceed - row is locked
    cart_item = CartItem.objects.create(...)
```

---

## 11. Middleware and Request Lifecycle

### Middleware Execution Order

```
Request -> [Security] -> [Session] -> [CORS] -> [Common] -> [CSRF] -> [Auth] -> [Messages] -> [Clickjacking] -> View

View -> [Clickjacking] -> [Messages] -> [Auth] -> [CSRF] -> [Common] -> [CORS] -> [Session] -> [Security] -> Response
```

### Custom Middleware Purpose

Currently no custom middleware, but common uses:

| Purpose | Implementation |
|---------|----------------|
| Request logging | Log method, path, user, response time |
| IP blocking | Check against blocklist |
| Rate limiting | Track request count per IP |

### Full Request Lifecycle

```
1. Client sends HTTP request
    |
2. [Security Middleware] - Adds security headers
    |
3. [Session Middleware] - Loads session if cookie present
    |
4. [CORS Middleware] - Handles preflight, adds CORS headers
    |
5. [Auth Middleware] - Loads user from JWT token
    |
6. [URL Router] - Matches path to view
    |
7. [DRF View] - Instantiates view class
    |
8. [Permission] - Checks has_permission()
    |
9. [Throttle] - Checks rate limit
    |
10. [View Method] - Runs get(), post(), etc.
    |
11. [Serializer] - Validates input, serializes output
    |
12. [Response] - JSON response sent back
```

### Error Handling in Lifecycle

```python
# In config/exception_handlers.py
def custom_exception_handler(exc, context):
    # First, try DRF's default handler
    response = exception_handler(exc, context)

    if response is not None:
        # Standardize response format
        response.data = {
            "error": True,
            "status_code": response.status_code,
            "message": get_error_message(exc),
            "details": response.data,
        }
        return response

    # Handle non-DRF exceptions
    if isinstance(exc, Http404):
        return Response({"error": "Not found"}, status=404)

    # Log and return generic error
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return Response({"error": "Internal server error"}, status=500)
```

---

## 12. Permissions and Security

### Permission Classes

```python
# Role-based
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "CUSTOMER"

# Object-level
class IsProductOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.shopkeeper == request.user
```

### Role-Based Access Summary

| Endpoint | Admin | Shopkeeper | Customer | Anonymous |
|----------|-------|------------|----------|-----------|
| List products | Read | Read | Read | Read |
| Create product | No | Yes (verified) | No | No |
| Edit product | No | Own only | No | No |
| View cart | No | No | Yes | No |
| Place order | No | No | Yes | No |
| Verify shopkeeper | Yes | No | No | No |

### Object-Level Permissions

```python
class IsAddressOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

# In view:
class AddressViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAddressOwner]

    def get_queryset(self):
        # Additional safety: Filter by user at queryset level
        return Address.objects.filter(user=self.request.user)
```

### Security Measures

| Attack | Prevention |
|--------|------------|
| SQL Injection | ORM parameterizes all queries |
| XSS | DRF escapes output by default |
| CSRF | Token validation on state-changing requests |
| Brute Force | Rate limiting (5 attempts/minute for auth) |
| Clickjacking | X-Frame-Options header |
| Password Breach | Bcrypt hashing, validation rules |
| Session Hijacking | Short token lifetime, session tracking |

---

## 13. Error Handling and Validation

### Global Exception Handling

All errors return JSON:
```json
{
    "error": true,
    "status_code": 400,
    "message": "Validation failed",
    "details": {
        "email": ["This email is already registered"]
    }
}
```

**Why Global Handler**:
- Consistent format across all endpoints
- Never return HTML (API-only backend)
- Centralized logging

### Validation Layering

```
1. [Model Field Validators]
   - Basic format validation
   - Runs on save()

2. [Serializer Field Validation]
   - validate_<field>() methods
   - Runs before validate()

3. [Serializer Object Validation]
   - validate() method
   - Cross-field validation
   - Business rules

4. [View Validation]
   - Permission checks
   - Custom checks
```

### Why Validation Is Not Done in Views

**Problem**:
```python
# BAD: Validation in view
def post(self, request):
    if not request.data.get("email"):
        return Response({"error": "Email required"}, 400)
    if "@" not in request.data["email"]:
        return Response({"error": "Invalid email"}, 400)
    # ... more validation
```

**Issues**:
- Duplicated across views
- Not reusable
- Easy to miss validations

**Solution**: Serializer handles all validation
```python
class UserSerializer:
    email = serializers.EmailField(required=True)  # Auto-validates

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("Email already registered")
        return value
```

---

## 14. Payment Flow

### Current Implementation

Payment is not fully implemented. Placeholder structure:

```python
class Order:
    payment_status = models.CharField(choices=[
        "PENDING",   # Awaiting payment
        "PAID",      # Payment confirmed
        "FAILED",    # Payment failed
        "REFUNDED",  # Order refunded
    ])
```

### Planned Flow (Stripe/Razorpay)

```
1. [Checkout] Create order with PENDING status
    |
2. [Create Payment Intent] Get client_secret from payment gateway
    |
3. [Frontend] Collect card details, submit to gateway
    |
4. [Webhook] Payment gateway sends confirmation
    |
5. [Verify] Verify webhook signature
    |
6. [Update] Set payment_status = PAID, release inventory
```

### Security Concerns

- Never log card numbers
- Verify webhook signatures (prevent fake confirmations)
- Use HTTPS only
- Payment logic in atomic transaction

## 16. Key Concepts Learned

### Django Concepts

- Custom User model with AbstractBaseUser
- Model Managers for filtered querysets
- Signals for decoupled logic (post_save)
- Abstract base classes for DRY models
- Database indexing for performance
- Migration management

### DRF Concepts

- ViewSets and routers for RESTful APIs
- Serializers for validation and transformation
- Custom permissions (permission_classes)
- Pagination strategies (Page vs Cursor)
- Exception handling customization
- Throttling for rate limiting

### Backend Engineering Principles

- Service layer for business logic separation
- Atomic transactions for data consistency
- N+1 query prevention with prefetch_related
- Soft delete for data preservation
- Environment-based configuration
- Structured error responses

---

## 17. Future Improvements

### Caching (Redis)

```python
# Cache product detail
@cache_page(60 * 15)  # 15 minutes
def retrieve(self, request, pk):
    ...

# Cache invalidation on update
def perform_update(self, serializer):
    cache.delete(f"product_{self.kwargs['pk']}")
    serializer.save()
```

### Async Tasks (Celery)

```python
# Email should not block request
@shared_task
def send_verification_email_task(user_id):
    user = User.objects.get(id=user_id)
    EmailService.send_verification_email(user)

# In registration:
send_verification_email_task.delay(user.id)
```

### Rate Limiting Improvements

- Per-endpoint limits
- IP-based limits for anonymous
- Token bucket algorithm

### Event-Driven Architecture

```python
# Events
ORDER_CREATED = "order.created"
PAYMENT_RECEIVED = "payment.received"

# Listeners
@event.listen(ORDER_CREATED)
def notify_shopkeeper(order):
    ...

@event.listen(PAYMENT_RECEIVED)
def release_inventory(order):
    ...
```

### Microservices Readiness

If needed, these would be good candidates:
- **Auth Service**: User management, tokens
- **Product Service**: Catalog, search
- **Order Service**: Cart, checkout, orders
- **Notification Service**: Email, SMS, push

---

## Document Version

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 2026 | Initial documentation |

---

*This document was created to provide complete understanding of the system architecture. For code-level details, refer to the source files with their inline documentation.*
