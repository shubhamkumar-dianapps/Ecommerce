"""
User Registration Serializers

Role-specific serializers for customer and shopkeeper registration.
Uses mixins and custom fields for DRY principles.
"""

from typing import Dict, Any
from rest_framework import serializers
from apps.accounts.models import User, CustomerProfile, ShopKeeperProfile
from apps.accounts import constants
from apps.accounts.fields import (
    PasswordField,
    PasswordConfirmField,
    GSTNumberField,
    FullNameField,
    ShopNameField,
    EmailField,
    PhoneField,
)
from apps.accounts.serializer_mixins import (
    PasswordConfirmationMixin,
    ProfileCreationMixin,
)


class BaseRegistrationSerializer(
    PasswordConfirmationMixin, serializers.ModelSerializer
):
    """
    Base serializer for user registration.

    Includes common fields and password confirmation logic.
    """

    email = EmailField()
    phone = PhoneField()
    password = PasswordField()
    password_confirm = PasswordConfirmField()

    class Meta:
        model = User
        fields = ("email", "phone", "password", "password_confirm")


class CustomerRegistrationSerializer(BaseRegistrationSerializer, ProfileCreationMixin):
    """
    Serializer for customer registration.

    Required fields: email, phone, password, password_confirm, full_name
    """

    full_name = FullNameField()
    profile_fields = ["full_name"]

    class Meta(BaseRegistrationSerializer.Meta):
        fields = BaseRegistrationSerializer.Meta.fields + ("full_name",)

    def get_profile_model(self) -> type:
        """Return CustomerProfile model class"""
        return CustomerProfile

    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        Create customer user and update profile.

        Args:
            validated_data: Validated serializer data

        Returns:
            Created User instance
        """
        # Extract profile data
        profile_data = self.extract_profile_data(validated_data)

        # Create user with CUSTOMER role
        user = User.objects.create_user(
            email=validated_data["email"],
            phone=validated_data["phone"],
            role=User.Role.CUSTOMER,
            password=validated_data["password"],
        )

        # Update profile (created by signal)
        self.update_profile(user, profile_data)

        return user


class ShopkeeperRegistrationSerializer(
    BaseRegistrationSerializer, ProfileCreationMixin
):
    """
    Serializer for shopkeeper registration.

    Required fields: email, phone, password, password_confirm, shop_name, gst_number
    Note: Shopkeeper accounts require manual verification by admin.
    """

    shop_name = ShopNameField()
    gst_number = GSTNumberField()
    profile_fields = ["shop_name", "gst_number"]

    class Meta(BaseRegistrationSerializer.Meta):
        fields = BaseRegistrationSerializer.Meta.fields + ("shop_name", "gst_number")

    def get_profile_model(self) -> type:
        """Return ShopKeeperProfile model class"""
        return ShopKeeperProfile

    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        Create shopkeeper user and update profile.

        Args:
            validated_data: Validated serializer data

        Returns:
            Created User instance
        """
        # Extract profile data
        profile_data = self.extract_profile_data(validated_data)

        # Create user with SHOPKEEPER role
        user = User.objects.create_user(
            email=validated_data["email"],
            phone=validated_data["phone"],
            role=User.Role.SHOPKEEPER,
            password=validated_data["password"],
        )

        # Update profile (created by signal)
        # Note: is_verified is False by default, admin needs to verify
        self.update_profile(user, profile_data)

        return user


class LegacyRegisterSerializer(serializers.ModelSerializer):
    """
    DEPRECATED: Legacy registration serializer.

    Use CustomerRegistrationSerializer or ShopkeeperRegistrationSerializer instead.
    This is kept for backward compatibility only.
    """

    password = PasswordField()
    shop_name = serializers.CharField(
        max_length=constants.NAME_MAX_LENGTH, required=False, allow_blank=True
    )
    gst_number = serializers.CharField(
        max_length=constants.GST_NUMBER_LENGTH, required=False, allow_blank=True
    )
    full_name = serializers.CharField(
        max_length=constants.NAME_MAX_LENGTH, required=False, allow_blank=True
    )

    class Meta:
        model = User
        fields = (
            "email",
            "phone",
            "role",
            "password",
            "shop_name",
            "gst_number",
            "full_name",
        )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate role-specific requirements.

        Args:
            attrs: Input data dictionary

        Returns:
            Validated data

        Raises:
            ValidationError: If validation fails
        """
        role = attrs.get("role")

        # Prevent admin registration via API
        if role == User.Role.ADMIN:
            raise serializers.ValidationError(constants.ADMIN_REGISTRATION_FORBIDDEN)

        if role == User.Role.SHOPKEEPER:
            if not attrs.get("shop_name") or not attrs.get("gst_number"):
                raise serializers.ValidationError(
                    "Shop name and GST number are required for shopkeepers."
                )
        elif role == User.Role.CUSTOMER:
            if not attrs.get("full_name"):
                raise serializers.ValidationError(
                    "Full name is required for customers."
                )

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        Create user with legacy flow.

        Args:
            validated_data: Validated data dictionary

        Returns:
            Created User instance
        """
        shop_name = validated_data.pop("shop_name", None)
        gst_number = validated_data.pop("gst_number", None)
        full_name = validated_data.pop("full_name", None)

        user = User.objects.create_user(**validated_data)

        # Profile is created by signal - update directly without extra SELECT
        if user.role == User.Role.SHOPKEEPER:
            ShopKeeperProfile.objects.filter(user=user).update(
                shop_name=shop_name, gst_number=gst_number
            )
        elif user.role == User.Role.CUSTOMER:
            CustomerProfile.objects.filter(user=user).update(full_name=full_name)

        return user
