"""
Address Validators

Validation functions for address-related data.
"""

import re
from django.core.exceptions import ValidationError
from apps.addresses import constants


def validate_postal_code(value: str, country: str = constants.DEFAULT_COUNTRY) -> None:
    """
    Validate postal code format based on country.

    Args:
        value: Postal code to validate
        country: Country name (default: India)

    Raises:
        ValidationError: If postal code format is invalid

    Examples:
        >>> validate_postal_code("110001", "India")  # Valid
        >>> validate_postal_code("12345", "United States")  # Valid
        >>> validate_postal_code("ABC", "India")  # Raises ValidationError
    """
    if not value:
        raise ValidationError(constants.POSTAL_CODE_REQUIRED)

    # Remove spaces for validation
    cleaned_value = value.replace(" ", "")

    # Check length constraints
    if len(cleaned_value) < constants.MIN_POSTAL_CODE_LENGTH:
        raise ValidationError(
            f"Postal code must be at least {constants.MIN_POSTAL_CODE_LENGTH} characters"
        )

    if len(cleaned_value) > constants.MAX_POSTAL_CODE_LENGTH:
        raise ValidationError(
            f"Postal code cannot exceed {constants.MAX_POSTAL_CODE_LENGTH} characters"
        )

    # Country-specific validation
    if country in constants.POSTAL_CODE_PATTERNS:
        pattern = constants.POSTAL_CODE_PATTERNS[country]
        if not re.match(pattern, value, re.IGNORECASE):
            raise ValidationError(f"{constants.INVALID_POSTAL_CODE} for {country}")


def validate_country(value: str) -> None:
    """
    Validate that country is supported.

    Args:
        value: Country name

    Raises:
        ValidationError: If country is not in supported list

    Examples:
        >>> validate_country("India")  # Valid
        >>> validate_country("Mars")  # Raises ValidationError
    """
    if value not in constants.SUPPORTED_COUNTRIES:
        raise ValidationError(
            f"{constants.INVALID_COUNTRY}. Supported countries: "
            f"{', '.join(constants.SUPPORTED_COUNTRIES)}"
        )


def validate_city(value: str) -> None:
    """
    Validate city name.

    Args:
        value: City name

    Raises:
        ValidationError: If city name is invalid
    """
    if not value or not value.strip():
        raise ValidationError("City name is required")

    if len(value.strip()) < 2:
        raise ValidationError("City name must be at least 2 characters")

    # Only allow letters, spaces, hyphens, and apostrophes
    if not re.match(r"^[a-zA-Z\s\-']+$", value):
        raise ValidationError("City name contains invalid characters")


def validate_state(value: str) -> None:
    """
    Validate state name.

    Args:
        value: State name

    Raises:
        ValidationError: If state name is invalid
    """
    if not value or not value.strip():
        raise ValidationError("State name is required")

    if len(value.strip()) < 2:
        raise ValidationError("State name must be at least 2 characters")

    # Only allow letters, spaces, hyphens, and apostrophes
    if not re.match(r"^[a-zA-Z\s\-']+$", value):
        raise ValidationError("State name contains invalid characters")
