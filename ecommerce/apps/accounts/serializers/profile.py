"""
User Profile Serializers

Serializers that return user data with nested profile information.
"""

from rest_framework import serializers
from apps.accounts.models import User, AdminProfile, ShopKeeperProfile, CustomerProfile
from apps.addresses.serializers import AddressListSerializer


class AdminProfileNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for admin profile"""

    class Meta:
        model = AdminProfile
        fields = ["id", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ShopKeeperProfileNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for shopkeeper profile"""

    class Meta:
        model = ShopKeeperProfile
        fields = [
            "id",
            "shop_name",
            "gst_number",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_verified", "created_at", "updated_at"]


class CustomerProfileNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for customer profile"""

    class Meta:
        model = CustomerProfile
        fields = ["id", "full_name"]
        read_only_fields = ["id"]


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Base user profile serializer.

    Returns user data with nested profile based on role and all addresses.
    """

    profile = serializers.SerializerMethodField()
    addresses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "role",
            "email_verified",
            "is_active",
            "created_at",
            "updated_at",
            "profile",
            "addresses",
        ]
        read_only_fields = [
            "id",
            "email",
            "role",
            "email_verified",
            "created_at",
            "updated_at",
        ]

    def get_profile(self, obj):
        """Get profile data based on user role"""
        if obj.role == User.Role.ADMIN:
            return AdminProfileNestedSerializer(obj.adminprofile).data
        elif obj.role == User.Role.SHOPKEEPER:
            return ShopKeeperProfileNestedSerializer(obj.shopkeeperprofile).data
        elif obj.role == User.Role.CUSTOMER:
            return CustomerProfileNestedSerializer(obj.customerprofile).data
        return None

    def get_addresses(self, obj):
        """
        Get all addresses for the user.

        Returns:
            List of address data dictionaries
        """
        addresses = obj.addresses.all().order_by("-is_default", "-created_at")
        return AddressListSerializer(addresses, many=True).data

    def update(self, instance, validated_data):
        """Update user and profile data"""
        # Update user fields
        instance.phone = validated_data.get("phone", instance.phone)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.save()

        return super().update(instance, validated_data)


class AdminProfileSerializer(UserProfileSerializer):
    """Admin user profile serializer"""

    def update(self, instance, validated_data):
        """Update admin user"""
        instance = super().update(instance, validated_data)
        # No additional admin profile fields to update
        return instance


class ShopKeeperProfileSerializer(UserProfileSerializer):
    """Shopkeeper user profile serializer with profile updates"""

    shop_name = serializers.CharField(write_only=True, required=False)
    gst_number = serializers.CharField(write_only=True, required=False)

    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + ["shop_name", "gst_number"]

    def update(self, instance, validated_data):
        """Update shopkeeper user and profile"""
        # Extract profile fields
        shop_name = validated_data.pop("shop_name", None)
        gst_number = validated_data.pop("gst_number", None)

        # Update user
        instance = super().update(instance, validated_data)

        # Update profile
        profile = instance.shopkeeperprofile
        if shop_name:
            profile.shop_name = shop_name
        if gst_number:
            profile.gst_number = gst_number
        profile.save()

        return instance


class CustomerProfileSerializer(UserProfileSerializer):
    """Customer user profile serializer with profile updates"""

    full_name = serializers.CharField(write_only=True, required=False)

    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + ["full_name"]

    def update(self, instance, validated_data):
        """Update customer user and profile"""
        # Extract profile fields
        full_name = validated_data.pop("full_name", None)

        # Update user
        instance = super().update(instance, validated_data)

        # Update profile
        profile = instance.customerprofile
        if full_name:
            profile.full_name = full_name
        profile.save()

        return instance
