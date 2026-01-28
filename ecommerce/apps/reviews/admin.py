from django.contrib import admin
from apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "user",
        "rating",
        "is_verified_purchase",
        "is_approved",
        "created_at",
    )
    list_filter = ("rating", "is_verified_purchase", "is_approved", "created_at")
    search_fields = ("product__name", "user__email", "title", "comment")
    readonly_fields = ("created_at", "updated_at")
