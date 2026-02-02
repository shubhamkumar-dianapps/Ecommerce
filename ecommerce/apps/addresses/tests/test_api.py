"""
Tests for Address API Endpoints

Comprehensive tests for address CRUD operations and set-default action.
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.addresses.models import Address
from apps.addresses.tests.factories import AddressFactory
from apps.accounts.tests.factories import UserFactory


class AddressListAPITest(TestCase):
    """Test cases for address list endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory.create_customer()
        self.url = reverse("address-list")

    def test_list_addresses_authenticated(self):
        """Test listing addresses when authenticated."""
        AddressFactory.create_address(user=self.user)
        AddressFactory.create_address(user=self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_list_addresses_unauthenticated(self):
        """Test listing addresses without authentication fails."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_only_own_addresses(self):
        """Test that users only see their own addresses."""
        other_user = UserFactory.create_customer()
        AddressFactory.create_address(user=self.user)
        AddressFactory.create_address(user=other_user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.data["count"], 1)

    def test_filter_by_address_type(self):
        """Test filtering addresses by type."""
        AddressFactory.create_address(user=self.user, address_type="HOME")
        AddressFactory.create_address(user=self.user, address_type="WORK")

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {"address_type": "HOME"})

        self.assertEqual(response.data["count"], 1)


class AddressCreateAPITest(TestCase):
    """Test cases for address create endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory.create_customer()
        self.url = reverse("address-list")

    def test_create_address_success(self):
        """Test successful address creation."""
        self.client.force_authenticate(user=self.user)

        data = {
            "address_type": "HOME",
            "address_line_1": "123 Main Street",
            "city": "Mumbai",
            "state": "Maharashtra",
            "postal_code": "400001",
            "country": "India",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("address", response.data)

    def test_create_address_unauthenticated(self):
        """Test creating address without authentication fails."""
        data = {
            "address_type": "HOME",
            "address_line_1": "123 Main Street",
            "city": "Mumbai",
            "state": "Maharashtra",
            "postal_code": "400001",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_address_invalid_postal_code(self):
        """Test creating address with invalid postal code fails."""
        self.client.force_authenticate(user=self.user)

        data = {
            "address_type": "HOME",
            "address_line_1": "123 Main Street",
            "city": "Mumbai",
            "state": "Maharashtra",
            "postal_code": "INVALID",
            "country": "India",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_address_missing_required_field(self):
        """Test creating address without required fields fails."""
        self.client.force_authenticate(user=self.user)

        data = {
            "address_type": "HOME",
            # Missing address_line_1
            "city": "Mumbai",
            "state": "Maharashtra",
            "postal_code": "400001",
        }

        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AddressDetailAPITest(TestCase):
    """Test cases for address detail endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory.create_customer()
        self.address = AddressFactory.create_address(user=self.user)
        self.url = reverse("address-detail", kwargs={"pk": self.address.pk})

    def test_get_address_detail(self):
        """Test getting address detail."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.address.id)

    def test_get_other_user_address_fails(self):
        """Test getting another user's address fails."""
        other_user = UserFactory.create_customer()
        self.client.force_authenticate(user=other_user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_address(self):
        """Test updating an address."""
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(self.url, {"city": "Delhi"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.address.refresh_from_db()
        self.assertEqual(self.address.city, "Delhi")

    def test_delete_address(self):
        """Test deleting an address."""
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Address.objects.filter(pk=self.address.pk).exists())

    def test_delete_default_address_fails(self):
        """Test deleting default address fails."""
        self.address.is_default = True
        self.address.save()

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AddressSetDefaultAPITest(TestCase):
    """Test cases for set-default action."""

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory.create_customer()
        self.address = AddressFactory.create_address(user=self.user, is_default=False)
        self.url = reverse("address-set-default", kwargs={"pk": self.address.pk})

    def test_set_default_success(self):
        """Test setting address as default."""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.address.refresh_from_db()
        self.assertTrue(self.address.is_default)

    def test_set_default_unsets_previous(self):
        """Test that setting new default unsets the old one."""
        old_default = AddressFactory.create_address(user=self.user, is_default=True)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        old_default.refresh_from_db()
        self.assertFalse(old_default.is_default)

    def test_set_default_other_user_fails(self):
        """Test setting another user's address as default fails."""
        other_user = UserFactory.create_customer()
        self.client.force_authenticate(user=other_user)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
