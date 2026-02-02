"""
Test Factories for Accounts App

Reusable factories for creating test users and profiles.
"""

from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory:
    """Factory for creating test users."""

    _counter = 0

    @classmethod
    def _get_unique_id(cls):
        cls._counter += 1
        return cls._counter

    @classmethod
    def create_customer(
        cls,
        email: str = None,
        password: str = "TestPass123!",
        full_name: str = "Test Customer",
        is_active: bool = True,
        email_verified: bool = True,
    ) -> User:
        """Create a test customer user."""
        unique_id = cls._get_unique_id()
        if email is None:
            email = f"customer{unique_id}@test.com"

        user = User.objects.create_user(
            email=email,
            phone=f"+9198765432{unique_id:02d}",
            password=password,
            role=User.Role.CUSTOMER,
        )
        user.is_active = is_active
        user.email_verified = email_verified
        user.save()

        # Update profile - must refresh user instance first
        user.refresh_from_db()
        if hasattr(user, "customerprofile"):
            user.customerprofile.full_name = full_name
            user.customerprofile.save()

        return user

    @classmethod
    def create_shopkeeper(
        cls,
        email: str = None,
        password: str = "TestPass123!",
        shop_name: str = "Test Shop",
        gst_number: str = None,
        is_verified: bool = True,
        is_active: bool = True,
    ) -> User:
        """Create a test shopkeeper user."""
        unique_id = cls._get_unique_id()
        if email is None:
            email = f"shopkeeper{unique_id}@test.com"
        if gst_number is None:
            gst_number = f"22AAAAA{unique_id:04d}A1Z5"

        user = User.objects.create_user(
            email=email,
            phone=f"+9187654321{unique_id:02d}",
            password=password,
            role=User.Role.SHOPKEEPER,
        )
        user.is_active = is_active
        user.save()

        # Update profile - must refresh user instance first
        user.refresh_from_db()
        if hasattr(user, "shopkeeperprofile"):
            user.shopkeeperprofile.shop_name = shop_name
            user.shopkeeperprofile.gst_number = gst_number
            user.shopkeeperprofile.is_verified = is_verified
            user.shopkeeperprofile.save()

        return user

    @classmethod
    def create_admin(
        cls,
        email: str = None,
        password: str = "AdminPass123!",
    ) -> User:
        """Create a test admin user."""
        unique_id = cls._get_unique_id()
        if email is None:
            email = f"admin{unique_id}@test.com"

        user = User.objects.create_superuser(
            email=email,
            phone=f"+9176543210{unique_id:02d}",
            password=password,
            role=User.Role.ADMIN,
        )
        return user
