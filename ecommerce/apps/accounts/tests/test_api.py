"""
Tests for Account API Endpoints

Comprehensive tests for registration, login, profile, and session endpoints.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.accounts.tests.factories import UserFactory

User = get_user_model()


class CustomerRegistrationAPITest(TestCase):
    """Test cases for customer registration endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("register_customer")

    def test_register_customer_success(self):
        """Test successful customer registration."""
        data = {
            "email": "newcustomer@example.com",
            "phone": "+919876543210",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "New Customer",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], "newcustomer@example.com")

    def test_register_customer_duplicate_email(self):
        """Test registration with duplicate email fails."""
        UserFactory.create_customer(email="existing@example.com")

        data = {
            "email": "existing@example.com",
            "phone": "+919876543211",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "Test User",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_customer_password_mismatch(self):
        """Test registration with mismatched passwords fails."""
        data = {
            "email": "test@example.com",
            "phone": "+919876543210",
            "password": "SecurePass123!",
            "password_confirm": "DifferentPass123!",
            "full_name": "Test User",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_customer_weak_password(self):
        """Test registration with weak password fails."""
        data = {
            "email": "test@example.com",
            "phone": "+919876543210",
            "password": "123",
            "password_confirm": "123",
            "full_name": "Test User",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_customer_invalid_phone(self):
        """Test registration with invalid phone fails."""
        data = {
            "email": "test@example.com",
            "phone": "12345",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "full_name": "Test User",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ShopkeeperRegistrationAPITest(TestCase):
    """Test cases for shopkeeper registration endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("register_shopkeeper")

    def test_register_shopkeeper_success(self):
        """Test successful shopkeeper registration."""
        data = {
            "email": "shopkeeper@example.com",
            "phone": "+919876543210",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "shop_name": "Test Shop",
            "gst_number": "22AAAAA0000A1Z5",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)

    def test_register_shopkeeper_missing_gst(self):
        """Test registration without GST number fails."""
        data = {
            "email": "shopkeeper@example.com",
            "phone": "+919876543210",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "shop_name": "Test Shop",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPITest(TestCase):
    """Test cases for login endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("login")
        self.user = UserFactory.create_customer(
            email="login@example.com", password="TestPass123!"
        )

    def test_login_success(self):
        """Test successful login."""
        data = {"email": "login@example.com", "password": "TestPass123!"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

    def test_login_wrong_password(self):
        """Test login with wrong password."""
        data = {"email": "login@example.com", "password": "WrongPassword123!"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_login_nonexistent_user(self):
        """Test login with non-existent email."""
        data = {"email": "nonexistent@example.com", "password": "TestPass123!"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_login_inactive_user(self):
        """Test login with inactive user."""

        data = {"email": "inactive@example.com", "password": "TestPass123!"}

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileAPITest(TestCase):
    """Test cases for profile endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("profile")
        self.user = UserFactory.create_customer(full_name="Test User")

    def test_get_profile_authenticated(self):
        """Test getting profile when authenticated."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_get_profile_unauthenticated(self):
        """Test getting profile without authentication fails."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile(self):
        """Test updating profile."""
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            self.url, {"full_name": "Updated Name"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TokenRefreshAPITest(TestCase):
    """Test cases for token refresh endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.refresh_url = reverse("token_refresh")
        self.login_url = reverse("login")
        self.user = UserFactory.create_customer(
            email="refresh@example.com", password="TestPass123!"
        )

    def test_token_refresh_success(self):
        """Test successful token refresh."""
        # First login to get tokens
        login_response = self.client.post(
            self.login_url,
            {"email": "refresh@example.com", "password": "TestPass123!"},
            format="json",
        )
        refresh_token = login_response.data["refresh"]

        # Then refresh the token
        response = self.client.post(
            self.refresh_url, {"refresh": refresh_token}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_token_refresh_invalid_token(self):
        """Test refresh with invalid token fails."""
        response = self.client.post(
            self.refresh_url, {"refresh": "invalid_token"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SessionsAPITest(TestCase):
    """Test cases for session management endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.sessions_url = reverse("active_sessions")
        self.user = UserFactory.create_customer()

    def test_list_sessions_authenticated(self):
        """Test listing sessions when authenticated."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.sessions_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_sessions_unauthenticated(self):
        """Test listing sessions without authentication fails."""
        response = self.client.get(self.sessions_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
