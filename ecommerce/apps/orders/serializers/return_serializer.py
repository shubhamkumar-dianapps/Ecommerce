"""
Return Request Serializers

Serializers for return request creation and display.
"""

from rest_framework import serializers
from apps.orders.models import ReturnRequest


class ReturnRequestSerializer(serializers.ModelSerializer):
    """Serializer for displaying return request details."""

    order_number = serializers.CharField(source="order.order_number", read_only=True)
    reason_display = serializers.CharField(source="get_reason_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ReturnRequest
        fields = [
            "id",
            "order_number",
            "reason",
            "reason_display",
            "description",
            "status",
            "status_display",
            "refund_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "refund_amount", "created_at", "updated_at"]


class ReturnRequestCreateSerializer(serializers.Serializer):
    """Serializer for creating a return request."""

    reason = serializers.ChoiceField(choices=ReturnRequest.ReturnReason.choices)
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000,
        help_text="Additional details about the return reason",
    )

    def validate_reason(self, value):
        """Validate reason is a valid choice."""
        valid_reasons = [choice[0] for choice in ReturnRequest.ReturnReason.choices]
        if value not in valid_reasons:
            raise serializers.ValidationError(
                f"Invalid reason. Must be one of: {', '.join(valid_reasons)}"
            )
        return value
