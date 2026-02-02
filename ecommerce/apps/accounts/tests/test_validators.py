"""
Tests for Account Validators

Comprehensive tests for password, phone, and GST validation.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.accounts.validators import (
    validate_password_strength,
    validate_phone_number,
    validate_gst_number,
)


class PasswordValidatorTest(TestCase):
    """Test cases for password strength validation."""

    def test_valid_password(self):
        """Test that a valid password passes validation."""
        # Should not raise
        validate_password_strength("SecurePass123!")

    def test_password_too_short(self):
        """Test that short password fails."""
        with self.assertRaises(ValidationError):
            validate_password_strength("Ab1!")

    def test_password_no_uppercase(self):
        """Test that password without uppercase fails."""
        with self.assertRaises(ValidationError):
            validate_password_strength("securepass123!")

    def test_password_no_lowercase(self):
        """Test that password without lowercase fails."""
        with self.assertRaises(ValidationError):
            validate_password_strength("SECUREPASS123!")

    def test_password_no_digit(self):
        """Test that password without digit fails."""
        with self.assertRaises(ValidationError):
            validate_password_strength("SecurePass!")

    def test_password_no_special_char(self):
        """Test that password without special character fails."""
        with self.assertRaises(ValidationError):
            validate_password_strength("SecurePass123")


class PhoneValidatorTest(TestCase):
    """Test cases for phone number validation."""

    def test_valid_indian_phone_with_country_code(self):
        """Test valid Indian phone with country code."""
        # Should not raise
        validate_phone_number("+919876543210")

    def test_valid_indian_phone_without_country_code(self):
        """Test valid Indian phone without country code."""
        # Should not raise (defaults to India)
        validate_phone_number("9876543210")

    def test_valid_international_phone(self):
        """Test valid international phone number."""
        # US number
        validate_phone_number("+14155552671")

    def test_invalid_phone_too_short(self):
        """Test that short phone number fails."""
        with self.assertRaises(ValidationError):
            validate_phone_number("12345")

    def test_invalid_phone_too_long(self):
        """Test that too long phone number fails."""
        with self.assertRaises(ValidationError):
            validate_phone_number("123456789012345678901234567890")

    def test_empty_phone(self):
        """Test that empty phone number fails."""
        with self.assertRaises(ValidationError):
            validate_phone_number("")


class GSTValidatorTest(TestCase):
    """Test cases for GST number validation."""

    def test_valid_gst_number(self):
        """Test valid GST number."""
        # Should not raise
        validate_gst_number("22AAAAA0000A1Z5")

    def test_gst_wrong_length(self):
        """Test GST number with wrong length fails."""
        with self.assertRaises(ValidationError):
            validate_gst_number("22AAAAA")

    def test_gst_invalid_format(self):
        """Test GST number with invalid format fails."""
        with self.assertRaises(ValidationError):
            validate_gst_number("ABCDEFGHIJKLMNO")

    def test_gst_lowercase_converted(self):
        """Test GST number validation handles lowercase."""
        # Lowercase should work as it's converted to uppercase
        validate_gst_number("22aaaaa0000a1z5")
