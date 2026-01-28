"""
Reviews App Admin

Admin interface for managing reviews, likes, and replies.
"""

from django.contrib import admin
from apps.reviews.models import Review, ReviewLike, ReviewReply


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for Review model"""

    list_display = [
        "id",
        "product",
        "user",
        "rating",
        "is_active",
        "is_owner_review",
        "helpful_count",
        "created_at",
    ]
    list_filter = ["is_active", "is_owner_review", "rating", "created_at"]
    search_fields = ["title", "comment", "user__email", "product__name"]
    readonly_fields = ["helpful_count", "is_owner_review", "created_at", "updated_at"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]

    fieldsets = (
        (
            "Review Information",
            {"fields": ("product", "user", "rating", "title", "comment")},
        ),
        (
            "Status",
            {"fields": ("is_active", "is_verified_purchase", "is_owner_review")},
        ),
        ("Metrics", {"fields": ("helpful_count",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    actions = ["activate_reviews", "deactivate_reviews"]

    @admin.action(description="Activate selected reviews")
    def activate_reviews(self, request, queryset):
        """Activate reviews that were deactivated"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} reviews activated successfully")

    @admin.action(description="Deactivate selected reviews")
    def deactivate_reviews(self, request, queryset):
        """Deactivate vulgar or inappropriate reviews"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} reviews deactivated successfully")


@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    """Admin interface for ReviewLike model"""

    list_display = ["id", "review", "user", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["review__title", "user__email"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]


@admin.register(ReviewReply)
class ReviewReplyAdmin(admin.ModelAdmin):
    """Admin interface for ReviewReply model"""

    list_display = ["id", "review", "user", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["comment", "user__email", "review__title"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]

    fieldsets = (
        ("Reply Information", {"fields": ("review", "user", "comment")}),
        ("Status", {"fields": ("is_active",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    actions = ["activate_replies", "deactivate_replies"]

    @admin.action(description="Activate selected replies")
    def activate_replies(self, request, queryset):
        """Activate replies that were deactivated"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} replies activated successfully")

    @admin.action(description="Deactivate selected replies")
    def deactivate_replies(self, request, queryset):
        """Deactivate inappropriate replies"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} replies deactivated successfully")
