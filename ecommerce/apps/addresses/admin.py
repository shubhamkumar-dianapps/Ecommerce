"""
Address Admin

Django admin configuration for addresses.
"""

from django.contrib import admin
from apps.addresses.models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
    Admin interface for Address model.

    Features:
    - Searchable by user email, city, state
    - Filterable by type, default status, country
    - List display shows key fields
    - Read-only timestamps
    - Custom actions
    """

    list_display = [
        "id",
        "get_user_email",
        "address_type",
        "city",
        "state",
        "country",
        "is_default",
        "created_at",
    ]

    list_filter = [
        "address_type",
        "is_default",
        "country",
        "created_at",
    ]

    search_fields = [
        "user__email",
        "city",
        "state",
        "postal_code",
        "address_line_1",
    ]

    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "full_address",
    ]

    fieldsets = (
        ("User", {"fields": ("user",)}),
        (
            "Address Details",
            {
                "fields": (
                    "address_type",
                    "address_line_1",
                    "address_line_2",
                    "city",
                    "state",
                    "postal_code",
                    "country",
                    "is_default",
                )
            },
        ),
        (
            "Computed",
            {
                "fields": ("full_address",),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("id", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = ["-is_default", "-created_at"]

    def get_user_email(self, obj):
        """Get user email for list display"""
        return obj.user.email

    get_user_email.short_description = "User"
    get_user_email.admin_order_field = "user__email"

    actions = ["make_default"]

    def make_default(self, request, queryset):
        """Admin action to set selected address as default"""
        if queryset.count() > 1:
            self.message_user(
                request,
                "Please select only one address to set as default",
                level="ERROR",
            )
            return

        address = queryset.first()
        address.set_as_default()
        self.message_user(
            request,
            f"Address {address.id} set as default for {address.user.email}",
            level="SUCCESS",
        )

    make_default.short_description = "Set selected address as default"
