"""
Test Factories for Addresses App

Reusable factories for creating test addresses.
"""

from apps.addresses.models import Address
from apps.accounts.tests.factories import UserFactory


class AddressFactory:
    """Factory for creating test addresses."""

    _counter = 0

    @classmethod
    def _get_unique_id(cls):
        cls._counter += 1
        return cls._counter

    @classmethod
    def create_address(
        cls,
        user=None,
        address_type: str = "HOME",
        address_line_1: str = "123 Test Street",
        address_line_2: str = "",
        city: str = "Mumbai",
        state: str = "Maharashtra",
        postal_code: str = "400001",
        country: str = "India",
        is_default: bool = False,
    ) -> Address:
        """Create a test address."""
        if user is None:
            user = UserFactory.create_customer()

        unique_id = cls._get_unique_id()

        address = Address.objects.create(
            user=user,
            address_type=address_type,
            address_line_1=f"{address_line_1} #{unique_id}",
            address_line_2=address_line_2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            is_default=is_default,
        )
        return address
