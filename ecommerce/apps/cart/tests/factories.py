"""
Cart App Tests - Test Factories

Factory classes for creating test data for cart tests.
"""

import uuid
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.products.models import Product, Category, Brand, Inventory
from apps.cart.models import Cart, CartItem
from apps.addresses.models import Address

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
        if hasattr(user, "shopkeeperprofile"):
            user.shopkeeperprofile.shop_name = f"Test Shop {uuid.uuid4().hex[:4]}"
            user.shopkeeperprofile.gst_number = f"GST{uuid.uuid4().hex[:12].upper()}"
            user.shopkeeperprofile.is_verified = is_verified
            user.shopkeeperprofile.save()
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
        stock: int = 100,
    ) -> Product:
        """Create a test product with inventory."""
        if shopkeeper is None:
            shopkeeper = UserFactory.create_shopkeeper()
        if category is None:
            category = ProductFactory.create_category()

        name = name or f"Product {uuid.uuid4().hex[:6]}"
        price = price or Decimal("99.99")

        product = Product.objects.create(
            shopkeeper=shopkeeper,
            name=name,
            slug=f"{name.lower().replace(' ', '-')}-{uuid.uuid4().hex[:4]}",
            description="Test product description",
            category=category,
            price=price,
            sku=f"SKU-{uuid.uuid4().hex[:8].upper()}",
            status=Product.ProductStatus.PUBLISHED,
        )

        # Create inventory for stock validation
        Inventory.objects.create(
            product=product,
            quantity=stock,
            reserved=0,
        )

        return product


class CartFactory:
    """Factory for creating test carts and cart items."""

    @staticmethod
    def create_cart(user: User = None) -> Cart:
        """Create a test cart."""
        if user is None:
            user = UserFactory.create_customer()
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    def create_cart_item(
        cart: Cart = None,
        product: Product = None,
        quantity: int = 1,
    ) -> CartItem:
        """Create a test cart item."""
        if cart is None:
            cart = CartFactory.create_cart()
        if product is None:
            product = ProductFactory.create_product()

        return CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity,
        )


class AddressFactory:
    """Factory for creating test addresses."""

    @staticmethod
    def create_address(
        user: User = None,
        address_type: str = "HOME",
        is_default: bool = True,
    ) -> Address:
        """Create a test address."""
        if user is None:
            user = UserFactory.create_customer()

        return Address.objects.create(
            user=user,
            address_type=address_type,
            address_line_1="123 Test Street",
            address_line_2="Apt 1",
            city="Mumbai",
            state="Maharashtra",
            postal_code="400001",
            country="India",
            is_default=is_default,
        )
