"""
Tests for Account Models

Comprehensive tests for User, CustomerProfile, and ShopkeeperProfile models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import CustomerProfile, ShopKeeperProfile, UserSession
from apps.accounts.tests.factories import UserFactory

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model."""

    def test_create_customer_user(self):
        """Test creating a customer user."""
        user = UserFactory.create_customer(email="customer@example.com")

        self.assertEqual(user.email, "customer@example.com")
        self.assertEqual(user.role, User.Role.CUSTOMER)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_shopkeeper_user(self):
        """Test creating a shopkeeper user."""
        user = UserFactory.create_shopkeeper(email="shopkeeper@example.com")

        self.assertEqual(user.email, "shopkeeper@example.com")
        self.assertEqual(user.role, User.Role.SHOPKEEPER)
        self.assertTrue(user.is_active)

    def test_create_admin_user(self):
        """Test creating an admin user."""
        user = UserFactory.create_admin(email="admin@example.com")

        self.assertEqual(user.email, "admin@example.com")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_email_is_username(self):
        """Test that email is used as the username field."""
        user = UserFactory.create_customer()
        self.assertEqual(user.email, user.get_username())

    def test_user_str_representation(self):
        """Test string representation of user."""
        user = UserFactory.create_customer(email="test@example.com")
        # User __str__ includes role
        self.assertIn("test@example.com", str(user))

    def test_email_normalized(self):
        """Test that email is normalized (lowercase)."""
        user = User.objects.create_user(
            email="Test@EXAMPLE.COM",
            phone="+919876543200",
            password="TestPass123!",
            role=User.Role.CUSTOMER,
        )
        self.assertEqual(user.email, "test@example.com")

    def test_create_user_without_email_raises_error(self):
        """Test creating user without email raises error."""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="",
                phone="+919876543210",
                password="TestPass123!",
                role=User.Role.CUSTOMER,
            )


class CustomerProfileTest(TestCase):
    """Test cases for CustomerProfile model."""

    def test_profile_created_on_user_creation(self):
        """Test that CustomerProfile is created when customer is created."""
        user = UserFactory.create_customer()
        self.assertTrue(hasattr(user, "customerprofile"))
        self.assertIsInstance(user.customerprofile, CustomerProfile)

    def test_profile_full_name(self):
        """Test profile full_name field."""
        user = UserFactory.create_customer(full_name="John Doe")
        self.assertEqual(user.customerprofile.full_name, "John Doe")

    def test_profile_str_representation(self):
        """Test string representation of profile."""
        user = UserFactory.create_customer(full_name="Jane Doe")
        self.assertIn("Jane Doe", str(user.customerprofile))


class ShopkeeperProfileTest(TestCase):
    """Test cases for ShopkeeperProfile model."""

    def test_profile_created_on_user_creation(self):
        """Test that ShopkeeperProfile is created when shopkeeper is created."""
        user = UserFactory.create_shopkeeper()
        self.assertTrue(hasattr(user, "shopkeeperprofile"))
        self.assertIsInstance(user.shopkeeperprofile, ShopKeeperProfile)

    def test_profile_shop_name_and_gst(self):
        """Test profile shop_name and gst_number fields."""
        user = UserFactory.create_shopkeeper(
            shop_name="My Shop", gst_number="22AAAAA0001A1Z5"
        )
        self.assertEqual(user.shopkeeperprofile.shop_name, "My Shop")
        self.assertEqual(user.shopkeeperprofile.gst_number, "22AAAAA0001A1Z5")

    def test_shopkeeper_verification_default(self):
        """Test that shopkeeper is not verified by default when is_verified=False."""
        user = UserFactory.create_shopkeeper(is_verified=False)
        self.assertFalse(user.shopkeeperprofile.is_verified)


class UserSessionTest(TestCase):
    """Test cases for UserSession model."""

    def test_create_session(self):
        """Test creating a user session."""
        user = UserFactory.create_customer()
        session = UserSession.objects.create(
            user=user,
            session_key="test_session_key_123",
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1",
        )

        self.assertEqual(session.user, user)
        self.assertTrue(session.is_active)
        self.assertIsNotNone(session.created_at)

    def test_session_revoke(self):
        """Test revoking a session."""
        user = UserFactory.create_customer()
        session = UserSession.objects.create(
            user=user,
            session_key="test_session_key_456",
            user_agent="Test Agent",
            ip_address="127.0.0.1",
        )

        session.invalidate()

        session.refresh_from_db()
        self.assertFalse(session.is_active)
