"""
Reusable Mixins for Serializers

DRY principle: Extract common serializer logic into reusable mixins.
"""

from typing import Dict, Any
from rest_framework import serializers
from apps.accounts import constants


class PasswordConfirmationMixin:
    """
    Mixin to add password confirmation validation to serializers.

    Adds password_confirm field and validates that it matches password field.
    """

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that password and password_confirm match.

        Args:
            attrs: Validated data dictionary

        Returns:
            Validated data with password_confirm removed

        Raises:
            ValidationError: If passwords don't match
        """
        password = attrs.get("password")
        password_confirm = attrs.pop("password_confirm", None)

        if password and password_confirm and password != password_confirm:
            raise serializers.ValidationError(
                {"password_confirm": constants.PASSWORD_MISMATCH_ERROR}
            )

        # Call parent validate if exists
        if hasattr(super(), "validate"):
            attrs = super().validate(attrs)

        return attrs


class ProfileCreationMixin:
    """
    Mixin to handle automatic profile updates after user creation.

    Subclasses must define:
    - profile_fields: List of field names that belong to profile
    - get_profile_model(): Method to get the profile model class
    """

    profile_fields = []

    def get_profile_model(self):
        """Override this in subclass to return profile model"""
        raise NotImplementedError("Subclass must implement get_profile_model()")

    def extract_profile_data(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract profile-specific fields from validated data.

        Args:
            validated_data: Full validated data dictionary

        Returns:
            Dictionary containing only profile fields
        """
        profile_data = {}
        for field in self.profile_fields:
            if field in validated_data:
                profile_data[field] = validated_data.pop(field)
        return profile_data

    def update_profile(self, user, profile_data: Dict[str, Any]) -> None:
        """
        Update user's profile with provided data.

        Args:
            user: User instance
            profile_data: Dictionary of profile field values
        """
        profile_model = self.get_profile_model()
        profile = getattr(user, profile_model.__name__.lower())

        for field, value in profile_data.items():
            setattr(profile, field, value)

        profile.save()
