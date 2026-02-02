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
    Validate phone numbers using the phonenumbers library.

    Policy: Accepts international phone numbers with India (IN) as the default
    region for parsing numbers without country code. This allows:
    - Indian numbers: "9876543210" or "+919876543210"
    - International numbers: "+14155552671" (US), "+447911123456" (UK)

    Note: The PHONE_REGEX in common.constants is NOT used here as it conflicts
    with international number support. Use this validator as the single source
    of truth for phone validation.

    Args:
        value: Phone number string to validate

    Raises:
        ValidationError: If phone number is invalid
    """
    if not value:
        raise ValidationError("Phone number is required")

    try:
        # Parse with India as default region for numbers without country code
        phone = phonenumbers.parse(value, "IN")

        # Check if the number is valid
        if not phonenumbers.is_valid_number(phone):
            raise ValidationError(
                "Invalid phone number. Please include country code for international numbers."
            )

    except phonenumbers.NumberParseException as e:
        raise ValidationError(f"Invalid phone number format: {str(e)}")


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

    Configurable requirements:
    - Minimum length (default: from common.constants.PASSWORD_MIN_LENGTH)
    - At least one uppercase letter (configurable)
    - At least one lowercase letter (configurable)
    - At least one digit (configurable)
    - At least one special character (configurable)

    Usage in settings.py:
        AUTH_PASSWORD_VALIDATORS = [
            {
                'NAME': 'apps.accounts.validators.EnhancedPasswordValidator',
                'OPTIONS': {
                    'min_length': 10,
                    'require_special': False,
                }
            },
        ]
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
        """
        Validate password against configured requirements.

        Uses instance configuration instead of delegating to validate_password_strength.
        """
        errors = []

        # Check minimum length
        if len(password) < self.min_length:
            errors.append(
                f"Password must be at least {self.min_length} characters long"
            )

        # Check for uppercase (if required)
        if self.require_uppercase and not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")

        # Check for lowercase (if required)
        if self.require_lowercase and not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")

        # Check for digit (if required)
        if self.require_digit and not re.search(r"\d", password):
            errors.append("Password must contain at least one digit")

        # Check for special character (if required)
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append(
                'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)'
            )

        if errors:
            raise ValidationError(errors)

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
