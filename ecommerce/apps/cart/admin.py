from django.contrib import admin
from apps.cart.models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("total_price",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "total_items", "subtotal", "created_at")
    inlines = [CartItemInline]
    readonly_fields = ("created_at", "updated_at", "total_items", "subtotal")
