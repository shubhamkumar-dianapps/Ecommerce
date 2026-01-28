"""
Enhanced Validators for Accounts App

All validation logic for accounts-related data.
Separated from field definitions for better organization and reusability.
"""

import re
from typing import Any
import phonenumbers
from django.core.exceptions import ValidationError
from apps.common import constants as common_constants
from apps.accounts import constants


def validate_phone_number(value: str) -> None:
    """
    Validate and normalize phone numbers using the phonenumbers library.
    Accepts international format.

    Args:
        value: Phone number string to validate

    Raises:
        ValidationError: If phone number is invalid
    """
    try:
        # Try to parse the phone number
        phone = phonenumbers.parse(value, None)

        # Check if the number is valid
        if not phonenumbers.is_valid_number(phone):
            raise ValidationError("Invalid phone number")

        # Optionally check if it matches the regex pattern as well
        if not re.match(common_constants.PHONE_REGEX, value):
            raise ValidationError("Phone number format doesn't match required pattern")

    except phonenumbers.NumberParseException:
        # If parsing fails, fall back to regex validation
        if not re.match(common_constants.PHONE_REGEX, value):
            raise ValidationError("Invalid phone number format")


def validate_gst_number(value: str) -> None:
    """
    Validate GST number format.

    GST format: 15 characters (2 digit state code + 10 digit PAN + 1 digit entity + 1 digit Z + 1 check digit)

    Args:
        value: GST number to validate

    Raises:
        ValidationError: If GST number is invalid
    """
    if len(value) != constants.GST_NUMBER_LENGTH:
        raise ValidationError(
            constants.GST_LENGTH_ERROR.format(length=constants.GST_NUMBER_LENGTH)
        )

    # GST format validation: 2-digit state code, PAN (10 alphanumeric), entity (1), Z (1), checksum (1)
    gst_pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
    if not re.match(gst_pattern, value.upper()):
        raise ValidationError(
            "Invalid GST number format. Expected format: 22AAAAA0000A1Z5"
        )


def validate_password_strength(value: str) -> None:
    """
    Validate password strength requirements.

    Args:
        value: Password to validate

    Raises:
        ValidationError: If password doesn't meet requirements
    """
    errors = []

    # Check minimum length
    if len(value) < common_constants.PASSWORD_MIN_LENGTH:
        errors.append(
            f"Password must be at least {common_constants.PASSWORD_MIN_LENGTH} characters long"
        )

    # Check for uppercase
    if not re.search(r"[A-Z]", value):
        errors.append("Password must contain at least one uppercase letter")

    # Check for lowercase
    if not re.search(r"[a-z]", value):
        errors.append("Password must contain at least one lowercase letter")

    # Check for digit
    if not re.search(r"\d", value):
        errors.append("Password must contain at least one digit")

    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        errors.append(
            'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)'
        )

    if errors:
        raise ValidationError(errors)


def validate_user_role(value: str) -> None:
    """
    Validate user role value.

    Args:
        value: Role string to validate

    Raises:
        ValidationError: If role is invalid
    """
    from apps.accounts.models import User

    valid_roles = [choice[0] for choice in User.Role.choices]
    if value not in valid_roles:
        raise ValidationError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")


class EnhancedPasswordValidator:
    """
    Enhanced password validator for Django's AUTH_PASSWORD_VALIDATORS.

    Checks for:
    - Minimum length
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """

    def __init__(
        self,
        min_length: int = None,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special: bool = True,
    ):
        self.min_length = min_length or common_constants.PASSWORD_MIN_LENGTH
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special

    def validate(self, password: str, user: Any = None) -> None:
        """Validate password against requirements"""
        validate_password_strength(password)

    def get_help_text(self) -> str:
        """Get help text for password requirements"""
        requirements = [f"at least {self.min_length} characters"]

        if self.require_uppercase:
            requirements.append("one uppercase letter")
        if self.require_lowercase:
            requirements.append("one lowercase letter")
        if self.require_digit:
            requirements.append("one digit")
        if self.require_special:
            requirements.append("one special character")

        return f"Your password must contain {', '.join(requirements)}."


# Keep the old validator for backward compatibility during transition
class CustomPasswordValidator:
    """DEPRECATED: Use EnhancedPasswordValidator instead"""

    def validate(self, password: str, user: Any = None) -> None:
        if len(password) < common_constants.PASSWORD_MIN_LENGTH:
            raise ValidationError(
                f"Password must be at least {common_constants.PASSWORD_MIN_LENGTH} characters"
            )

    def get_help_text(self) -> str:
        return f"Your password must contain at least {common_constants.PASSWORD_MIN_LENGTH} characters."
