from django.contrib import admin
from django.contrib import messages
from apps.orders.models import Order, OrderItem, ReturnRequest
from apps.orders.services.order_service import OrderService


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product_name",
        "product_sku",
        "unit_price",
        "quantity",
        "total_price",
    )
    can_delete = False


class ReturnRequestInline(admin.StackedInline):
    model = ReturnRequest
    extra = 0
    readonly_fields = ("created_at", "updated_at")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "status",
        "payment_status",
        "total",
        "created_at",
    )
    list_filter = ("status", "payment_status", "created_at")
    search_fields = ("order_number", "user__email")
    readonly_fields = ("order_number", "created_at", "updated_at", "subtotal", "total")
    inlines = [OrderItemInline, ReturnRequestInline]

    fieldsets = (
        (
            "Order Info",
            {"fields": ("order_number", "user", "created_at", "updated_at")},
        ),
        ("Addresses", {"fields": ("shipping_address", "billing_address")}),
        ("Pricing", {"fields": ("subtotal", "shipping_cost", "tax", "total")}),
        ("Status", {"fields": ("status", "payment_status")}),
        ("Notes", {"fields": ("customer_notes", "admin_notes")}),
    )


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    """Admin for managing return requests."""

    list_display = (
        "id",
        "order_number",
        "reason",
        "status",
        "refund_amount",
        "created_at",
    )
    list_filter = ("status", "reason", "created_at")
    search_fields = ("order__order_number", "order__user__email")
    readonly_fields = ("created_at", "updated_at")
    actions = ["approve_returns", "reject_returns", "mark_received", "process_refunds"]

    fieldsets = (
        ("Order Info", {"fields": ("order",)}),
        ("Return Details", {"fields": ("reason", "description")}),
        ("Status", {"fields": ("status", "refund_amount")}),
        ("Admin", {"fields": ("admin_notes", "created_at", "updated_at")}),
    )

    def order_number(self, obj):
        return obj.order.order_number

    order_number.short_description = "Order Number"

    @admin.action(description="Approve selected return requests")
    def approve_returns(self, request, queryset):
        """Approve selected return requests."""
        updated = queryset.filter(status=ReturnRequest.ReturnStatus.PENDING).update(
            status=ReturnRequest.ReturnStatus.APPROVED
        )
        self.message_user(
            request,
            f"{updated} return request(s) approved.",
            messages.SUCCESS,
        )

    @admin.action(description="Reject selected return requests")
    def reject_returns(self, request, queryset):
        """Reject selected return requests."""
        updated = queryset.filter(status=ReturnRequest.ReturnStatus.PENDING).update(
            status=ReturnRequest.ReturnStatus.REJECTED
        )
        self.message_user(
            request,
            f"{updated} return request(s) rejected.",
            messages.WARNING,
        )

    @admin.action(description="Mark as item received")
    def mark_received(self, request, queryset):
        """Mark return requests as item received."""
        updated = queryset.filter(status=ReturnRequest.ReturnStatus.APPROVED).update(
            status=ReturnRequest.ReturnStatus.RECEIVED
        )
        self.message_user(
            request,
            f"{updated} return request(s) marked as received.",
            messages.SUCCESS,
        )

    @admin.action(description="Process refunds for selected returns")
    def process_refunds(self, request, queryset):
        """Process refunds for approved/received return requests."""
        success_count = 0
        for return_request in queryset:
            success, message = OrderService.process_refund(return_request)
            if success:
                success_count += 1

        self.message_user(
            request,
            f"{success_count} refund(s) processed successfully.",
            messages.SUCCESS,
        )
