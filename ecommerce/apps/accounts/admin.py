from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.accounts.models import (
    User,
    AdminProfile,
    CustomerProfile,
    ShopKeeperProfile,
    EmailVerificationToken,
    UserSession,
    AuditLog,
)


class AdminProfileInline(admin.StackedInline):
    model = AdminProfile
    can_delete = False
    verbose_name_plural = "Admin Profile"
    fk_name = "user"


class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = "Customer Profile"
    fk_name = "user"


class ShopKeeperProfileInline(admin.StackedInline):
    model = ShopKeeperProfile
    can_delete = False
    verbose_name_plural = "ShopKeeper Profile"
    fk_name = "user"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "phone",
        "role",
        "email_verified",
        "is_active",
        "is_staff",
        "created_at",
    )
    list_filter = (
        "role",
        "email_verified",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
    )
    search_fields = ("email", "phone")
    ordering = ("-created_at",)
    actions = ["verify_emails"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("phone", "role")}),
        ("Verification", {"fields": ("email_verified",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important dates",
            {"fields": ("last_login", "created_at", "updated_at", "deleted_at")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "phone",
                    "role",
                    "password1",
                    "password2",
                    "email_verified",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    readonly_fields = ("last_login", "created_at", "updated_at")

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        inlines = []
        if obj.role == User.Role.ADMIN:
            inlines.append(AdminProfileInline(self.model, self.admin_site))
        elif obj.role == User.Role.CUSTOMER:
            inlines.append(CustomerProfileInline(self.model, self.admin_site))
        elif obj.role == User.Role.SHOPKEEPER:
            inlines.append(ShopKeeperProfileInline(self.model, self.admin_site))

        return inlines

    @admin.action(description="Verify selected users' emails")
    def verify_emails(self, request, queryset):
        count = queryset.update(email_verified=True)
        self.message_user(request, f"{count} user(s) verified successfully.")


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "department", "created_at")
    search_fields = ("user__email", "department")
    readonly_fields = ("created_at", "updated_at")


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "created_at")
    search_fields = ("user__email", "full_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ShopKeeperProfile)
class ShopKeeperProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "shop_name", "gst_number", "is_verified", "created_at")
    list_filter = ("is_verified",)
    search_fields = ("user__email", "shop_name", "gst_number")
    readonly_fields = ("created_at", "updated_at")
    actions = ["verify_shops"]

    @admin.action(description="Verify selected shops")
    def verify_shops(self, request, queryset):
        count = queryset.update(is_verified=True)
        self.message_user(request, f"{count} shop(s) verified successfully.")


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at", "expires_at", "is_used")
    list_filter = ("is_used", "created_at")
    search_fields = ("user__email",)
    readonly_fields = ("token", "created_at", "expires_at")
    ordering = ("-created_at",)


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "ip_address",
        "created_at",
        "last_activity",
        "is_active",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("user__email", "ip_address")
    readonly_fields = ("session_key", "created_at", "last_activity")
    ordering = ("-last_activity",)
    actions = ["invalidate_sessions"]

    @admin.action(description="Invalidate selected sessions")
    def invalidate_sessions(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} session(s) invalidated successfully.")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "ip_address", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__email", "ip_address")
    readonly_fields = (
        "user",
        "action",
        "ip_address",
        "user_agent",
        "metadata",
        "created_at",
    )
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        # Prevent manual creation of audit logs
        return False

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of audit logs
        return False
