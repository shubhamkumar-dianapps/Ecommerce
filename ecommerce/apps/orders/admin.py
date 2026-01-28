from django.contrib import admin
from apps.orders.models import Order, OrderItem


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
    inlines = [OrderItemInline]

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
