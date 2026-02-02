"""
Address Models

Production-ready address model with proper validation and constants.
"""

from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel
from apps.addresses import constants
from apps.addresses.validators import (
    validate_postal_code,
    validate_country,
    validate_city,
    validate_state,
)


class Address(TimeStampedModel):
    """
    User address model.

    Stores delivery/billing addresses for users. Each user can have multiple
    addresses with one marked as default.

    Features:
    - Multiple address types (Home, Work, Other)
    - Country-specific postal code validation
    - Only one default address per user (auto-managed)
    - Soft ordering by default status
    """

    class AddressType(models.TextChoices):
        """Address type choices"""

        HOME = "HOME", "Home"
        WORK = "WORK", "Work"
        OTHER = "OTHER", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
        help_text="User who owns this address",
    )

    address_type = models.CharField(
        max_length=constants.ADDRESS_TYPE_MAX_LENGTH,
        choices=AddressType.choices,
        default=AddressType.HOME,
        help_text="Type of address",
    )

    address_line_1 = models.CharField(
        max_length=constants.ADDRESS_LINE_MAX_LENGTH,
        help_text="Street address, P.O. box, company name",
    )

    address_line_2 = models.CharField(
        max_length=constants.ADDRESS_LINE_MAX_LENGTH,
        blank=True,
        help_text="Apartment, suite, unit, building, floor, etc.",
    )

    city = models.CharField(
        max_length=constants.CITY_MAX_LENGTH,
        validators=[validate_city],
        help_text="City or district",
    )

    state = models.CharField(
        max_length=constants.STATE_MAX_LENGTH,
        validators=[validate_state],
        help_text="State, province, or region",
    )

    postal_code = models.CharField(
        max_length=constants.POSTAL_CODE_MAX_LENGTH, help_text="ZIP or postal code"
    )

    country = models.CharField(
        max_length=constants.COUNTRY_MAX_LENGTH,
        default=constants.DEFAULT_COUNTRY,
        validators=[validate_country],
        help_text="Country name",
    )

    is_default = models.BooleanField(
        default=False, help_text="Primary address for deliveries"
    )

    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ["-is_default", "-created_at"]
        indexes = [
            models.Index(fields=["user", "is_default"]),
            models.Index(fields=["user", "address_type"]),
        ]

    def __str__(self) -> str:
        """
        Return string representation of address.

        Handles all user types (Customer, Shopkeeper, Admin).

        Returns:
            str: Formatted address string
        """
        # Get user display name based on role
        if hasattr(self.user, "customerprofile"):
            name = self.user.customerprofile.full_name
        elif hasattr(self.user, "shopkeeperprofile"):
            name = self.user.shopkeeperprofile.shop_name
        else:
            # For admin or users without profile
            name = self.user.email

        return f"{name} - {self.city}, {self.state}"

    def save(self, *args, **kwargs) -> None:
        """
        Save address with default address logic.

        If this address is marked as default, unset any existing
        default addresses for this user.

        Also validates postal code with country.

        Uses transaction + select_for_update to prevent race conditions
        where two addresses could briefly both be marked as default.
        """
        from django.db import transaction

        # Validate postal code for the country
        if self.postal_code and self.country:
            validate_postal_code(self.postal_code, self.country)

        # Ensure only one default address per user (atomic operation)
        if self.is_default:
            with transaction.atomic():
                # Lock all user's addresses to prevent race condition
                Address.objects.select_for_update().filter(
                    user=self.user, is_default=True
                ).exclude(pk=self.pk).update(is_default=False)
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def set_as_default(self) -> None:
        """
        Set this address as the default address.

        Automatically unsets any other default addresses for the user.

        Uses transaction + select_for_update to prevent race conditions.
        """
        from django.db import transaction

        if not self.is_default:
            with transaction.atomic():
                # Lock all user's addresses to prevent race condition
                Address.objects.select_for_update().filter(
                    user=self.user, is_default=True
                ).update(is_default=False)

                self.is_default = True
                self.save(update_fields=["is_default", "updated_at"])

    @property
    def full_address(self) -> str:
        """
        Get complete formatted address.

        Returns:
            str: Full address with all fields
        """
        parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.state,
            self.postal_code,
            self.country,
        ]
        return ", ".join(part for part in parts if part)
