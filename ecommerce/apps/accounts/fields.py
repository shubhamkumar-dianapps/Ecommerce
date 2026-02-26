"""
Enhanced Field Validators for Accounts App

Custom field classes with built-in validation for reuse across serializers.
"""

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from apps.accounts import constants
from apps.accounts.validators import (
    validate_gst_number,
    validate_password_strength,
    validate_phone_number,
)
from apps.accounts.models import User


class PasswordField(serializers.CharField):
    """Custom password field with built-in validation and styling"""

    def __init__(self, **kwargs):
        kwargs.setdefault("write_only", True)
        kwargs.setdefault("style", {"input_type": "password"})
        kwargs.setdefault("help_text", constants.PASSWORD_HELP_TEXT)
        kwargs.setdefault("validators", []).append(validate_password_strength)
        super().__init__(**kwargs)


class PasswordConfirmField(serializers.CharField):
    """Password confirmation field"""

    def __init__(self, **kwargs):
        kwargs.setdefault("write_only", True)
        kwargs.setdefault("style", {"input_type": "password"})
        kwargs.setdefault("help_text", constants.PASSWORD_CONFIRM_HELP_TEXT)
        super().__init__(**kwargs)


class GSTNumberField(serializers.CharField):
    """GST number field with validation"""

    def __init__(self, **kwargs):
        kwargs.setdefault("max_length", constants.GST_NUMBER_LENGTH)
        kwargs.setdefault(
            "help_text",
            constants.GST_HELP_TEXT.format(length=constants.GST_NUMBER_LENGTH),
        )
        kwargs.setdefault("validators", []).append(validate_gst_number)
        super().__init__(**kwargs)


class FullNameField(serializers.CharField):
    """Full name field with standardized config"""

    def __init__(self, **kwargs):
        kwargs.setdefault("max_length", constants.NAME_MAX_LENGTH)
        kwargs.setdefault("help_text", "Customer's full name")
        super().__init__(**kwargs)


class ShopNameField(serializers.CharField):
    """Shop name field with standardized config"""

    def __init__(self, **kwargs):
        kwargs.setdefault("max_length", constants.NAME_MAX_LENGTH)
        kwargs.setdefault("help_text", "Name of the shop/business")
        super().__init__(**kwargs)


class EmailField(serializers.EmailField):
    """Email field with standardized config and uniqueness validation"""

    def __init__(self, **kwargs):
        kwargs.setdefault("help_text", "Email address (must be unique)")
        # Add unique validator to catch duplicates at serializer level
        validators = kwargs.setdefault("validators", [])
        validators.append(
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with this email already exists.",
            )
        )
        super().__init__(**kwargs)


class PhoneField(serializers.CharField):
    """Phone number field with validation and uniqueness check"""

    def __init__(self, **kwargs):
        kwargs.setdefault("help_text", constants.PHONE_HELP_TEXT)
        # Add phone number validator
        validators = kwargs.setdefault("validators", [])
        validators.append(validate_phone_number)
        # Add unique validator to catch duplicates at serializer level
        validators.append(
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with this phone number already exists.",
            )
        )
        super().__init__(**kwargs)
