"""
Tests for Address Models

Comprehensive tests for Address model and its methods.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.addresses.models import Address
from apps.addresses.tests.factories import AddressFactory
from apps.accounts.tests.factories import UserFactory


class AddressModelTest(TestCase):
    """Test cases for Address model."""

    def setUp(self):
        self.user = UserFactory.create_customer()

    def test_create_address(self):
        """Test creating an address."""
        address = AddressFactory.create_address(user=self.user)

        self.assertEqual(address.user, self.user)
        self.assertEqual(address.address_type, "HOME")
        self.assertEqual(address.country, "India")
        self.assertFalse(address.is_default)

    def test_address_types(self):
        """Test different address types."""
        home = AddressFactory.create_address(user=self.user, address_type="HOME")
        work = AddressFactory.create_address(user=self.user, address_type="WORK")
        other = AddressFactory.create_address(user=self.user, address_type="OTHER")

        self.assertEqual(home.address_type, "HOME")
        self.assertEqual(work.address_type, "WORK")
        self.assertEqual(other.address_type, "OTHER")

    def test_address_str_representation(self):
        """Test string representation of address."""
        address = AddressFactory.create_address(
            user=self.user, city="Mumbai", state="Maharashtra"
        )

        str_repr = str(address)
        self.assertIn("Mumbai", str_repr)
        self.assertIn("Maharashtra", str_repr)

    def test_full_address_property(self):
        """Test full_address property."""
        address = AddressFactory.create_address(
            user=self.user,
            address_line_1="123 Main St",
            city="Mumbai",
            state="Maharashtra",
            postal_code="400001",
            country="India",
        )

        full = address.full_address

        self.assertIn("Mumbai", full)
        self.assertIn("Maharashtra", full)
        self.assertIn("400001", full)
        self.assertIn("India", full)


class AddressDefaultTest(TestCase):
    """Test cases for default address logic."""

    def setUp(self):
        self.user = UserFactory.create_customer()

    def test_first_address_can_be_default(self):
        """Test that first address can be set as default."""
        address = AddressFactory.create_address(user=self.user, is_default=True)
        self.assertTrue(address.is_default)

    def test_setting_new_default_unsets_old(self):
        """Test that setting new default unsets the old one."""
        addr1 = AddressFactory.create_address(user=self.user, is_default=True)
        addr2 = AddressFactory.create_address(user=self.user, is_default=True)

        addr1.refresh_from_db()
        addr2.refresh_from_db()

        self.assertFalse(addr1.is_default)
        self.assertTrue(addr2.is_default)

    def test_set_as_default_method(self):
        """Test set_as_default method."""
        addr1 = AddressFactory.create_address(user=self.user, is_default=True)
        addr2 = AddressFactory.create_address(user=self.user, is_default=False)

        addr2.set_as_default()

        addr1.refresh_from_db()
        addr2.refresh_from_db()

        self.assertFalse(addr1.is_default)
        self.assertTrue(addr2.is_default)

    def test_only_one_default_per_user(self):
        """Test that each user can only have one default address."""
        # Create 3 addresses, all trying to be default
        addr1 = AddressFactory.create_address(user=self.user, is_default=True)
        addr2 = AddressFactory.create_address(user=self.user, is_default=True)
        addr3 = AddressFactory.create_address(user=self.user, is_default=True)

        # Refresh all
        addr1.refresh_from_db()
        addr2.refresh_from_db()
        addr3.refresh_from_db()

        # Only one should be default
        defaults = [addr1.is_default, addr2.is_default, addr3.is_default]
        self.assertEqual(sum(defaults), 1)
        self.assertTrue(addr3.is_default)


class AddressValidationTest(TestCase):
    """Test cases for address validation."""

    def setUp(self):
        self.user = UserFactory.create_customer()

    def test_valid_indian_postal_code(self):
        """Test that valid Indian postal code passes."""
        address = AddressFactory.create_address(
            user=self.user, postal_code="400001", country="India"
        )
        self.assertEqual(address.postal_code, "400001")

    def test_invalid_postal_code_in_model_save(self):
        """Test that invalid postal code raises error."""
        with self.assertRaises(ValidationError):
            Address.objects.create(
                user=self.user,
                address_line_1="Test Street",
                city="Mumbai",
                state="Maharashtra",
                postal_code="INVALID",
                country="India",
            )


class AddressOrderingTest(TestCase):
    """Test cases for address ordering."""

    def setUp(self):
        self.user = UserFactory.create_customer()

    def test_default_ordering(self):
        """Test that addresses are ordered by default status and date."""

        addresses = list(Address.objects.filter(user=self.user))

        # Default should come first
        self.assertTrue(addresses[0].is_default)
