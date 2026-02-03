"""
Address Serializers

Production-ready serializers with proper validation and clean responses.
"""

from typing import Dict, Any
from rest_framework import serializers
from apps.addresses.models import Address


class AddressSerializer(serializers.ModelSerializer):
    """
    Comprehensive address serializer.

    Features:
    - Explicit field definitions (no __all__)
    - Proper validation
    - Help text for API documentation
    - Read-only fields for security
    """

    full_address = serializers.ReadOnlyField(help_text="Complete formatted address")

    class Meta:
        model = Address
        fields = [
            "id",
            "address_type",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "postal_code",
            "country",
            "is_default",
            "full_address",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "full_address"]

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate address data.

        Args:
            attrs: Validated attribute dictionary

        Returns:
            Dict: Validated and cleaned data

        Raises:
            ValidationError: If data is invalid or duplicate exists
        """
        # Ensure required fields are present
        if not attrs.get("address_line_1"):
            raise serializers.ValidationError(
                {"address_line_1": "Street address is required"}
            )

        # Validate postal code format based on country
        postal_code = attrs.get("postal_code")
        country = attrs.get("country", "India")

        if postal_code:
            from apps.addresses.validators import validate_postal_code
            from django.core.exceptions import ValidationError as DjangoValidationError

            try:
                validate_postal_code(postal_code, country)
            except DjangoValidationError as e:
                raise serializers.ValidationError(
                    {"postal_code": e.messages[0] if e.messages else str(e)}
                )

        # Check for duplicate address (only on create, not update)
        if not self.instance:
            request = self.context.get("request")
            if request and request.user.is_authenticated:
                existing = Address.objects.filter(
                    user=request.user,
                    address_line_1__iexact=attrs.get("address_line_1", ""),
                    city__iexact=attrs.get("city", ""),
                    postal_code=attrs.get("postal_code", ""),
                ).first()

                if existing:
                    raise serializers.ValidationError(
                        {
                            "non_field_errors": [
                                "An address with this street, city, and postal code already exists."
                            ],
                            "existing_address_id": str(existing.id),
                        }
                    )

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> Address:
        """
        Create new address.

        Automatically assigns current user from request context.

        Args:
            validated_data: Validated address data

        Returns:
            Address: Created address instance
        """
        # Set user from request context
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class AddressListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for address listings.

    Excludes timestamps for cleaner response in list views.
    """

    full_address = serializers.ReadOnlyField()

    class Meta:
        model = Address
        fields = [
            "id",
            "address_type",
            "address_line_1",
            "city",
            "state",
            "postal_code",
            "country",
            "is_default",
            "full_address",
        ]
        read_only_fields = ["id", "full_address"]


class SetDefaultSerializer(serializers.Serializer):
    """
    Serializer for set-default action.

    No input fields required - just validates the request.
    """

    def update(self, instance: Address, validated_data: Dict[str, Any]) -> Address:
        """
        Set address as default.

        Args:
            instance: Address to set as default
            validated_data: Validated data (empty)

        Returns:
            Address: Updated address instance
        """
        instance.set_as_default()
        return instance
