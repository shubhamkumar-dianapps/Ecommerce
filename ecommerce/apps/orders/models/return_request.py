"""
Return Request Model

Tracks customer return requests for delivered orders.
"""

import uuid
from django.db import models
from apps.common.models import TimeStampedModel


class ReturnRequest(TimeStampedModel):
    """
    Model to track return requests for orders.

    Flow: PENDING → APPROVED → RECEIVED → REFUNDED
          PENDING → REJECTED (if denied)
    """

    class ReturnStatus(models.TextChoices):
        PENDING = "PENDING", "Pending Review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        RECEIVED = "RECEIVED", "Item Received"
        REFUNDED = "REFUNDED", "Refunded"

    class ReturnReason(models.TextChoices):
        DEFECTIVE = "DEFECTIVE", "Defective/Damaged"
        WRONG_ITEM = "WRONG_ITEM", "Wrong Item Received"
        NOT_AS_DESCRIBED = "NOT_AS_DESCRIBED", "Not As Described"
        CHANGED_MIND = "CHANGED_MIND", "Changed Mind"
        OTHER = "OTHER", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="return_request",
    )
    reason = models.CharField(
        max_length=20,
        choices=ReturnReason.choices,
    )
    description = models.TextField(
        blank=True,
        help_text="Additional details about the return reason",
    )
    status = models.CharField(
        max_length=20,
        choices=ReturnStatus.choices,
        default=ReturnStatus.PENDING,
    )
    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount to be refunded (set when approved)",
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes for admin/shopkeeper",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Return Request"
        verbose_name_plural = "Return Requests"

    def __str__(self):
        return f"Return for Order {self.order.order_number} - {self.status}"

    @property
    def is_pending(self):
        return self.status == self.ReturnStatus.PENDING

    @property
    def is_approved(self):
        return self.status == self.ReturnStatus.APPROVED

    @property
    def is_refunded(self):
        return self.status == self.ReturnStatus.REFUNDED
