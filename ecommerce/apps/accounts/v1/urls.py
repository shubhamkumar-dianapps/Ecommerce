"""
API v1 URLs for Accounts App

All v1 endpoints are organized here for clear versioning.
"""

from django.urls import path
from apps.accounts.views.auth import (
    CustomerRegistrationView,
    ShopkeeperRegistrationView,
    LegacyRegisterView,
    LoginView,
)
from apps.accounts.views.profile import ProfileView
from apps.accounts.views.email_views import (
    VerifyEmailView,
    ResendVerificationEmailView,
)
from apps.accounts.views.session_views import (
    ActiveSessionsView,
    RevokeSessionView,
    RevokeAllSessionsView,
)
from apps.accounts.views.password_reset import (
    PasswordResetRequestView,
    PasswordResetConfirmView,
    EmailChangeRequestView,
    EmailChangeConfirmView,
)
from rest_framework_simplejwt.views import TokenRefreshView

# Authentication endpoints
auth_patterns = [
    path(
        "register/customer/",
        CustomerRegistrationView.as_view(),
        name="register_customer",
    ),
    path(
        "register/shopkeeper/",
        ShopkeeperRegistrationView.as_view(),
        name="register_shopkeeper",
    ),
    path(
        "register/", LegacyRegisterView.as_view(), name="register_legacy"
    ),  # Deprecated
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

# Profile endpoints
profile_patterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
]

# Email verification endpoints
email_patterns = [
    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path(
        "resend-verification/",
        ResendVerificationEmailView.as_view(),
        name="resend_verification",
    ),
]

# Session management endpoints
session_patterns = [
    path("sessions/", ActiveSessionsView.as_view(), name="active_sessions"),
    path("sessions/revoke/", RevokeSessionView.as_view(), name="revoke_session"),
    path(
        "sessions/revoke-all/",
        RevokeAllSessionsView.as_view(),
        name="revoke_all_sessions",
    ),
]

# Password reset endpoints
password_reset_patterns = [
    path(
        "password-reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]

# Email change endpoints
email_change_patterns = [
    path(
        "email-change/",
        EmailChangeRequestView.as_view(),
        name="email_change_request",
    ),
    path(
        "email-change/confirm/",
        EmailChangeConfirmView.as_view(),
        name="email_change_confirm",
    ),
]

# Combine all patterns
urlpatterns = (
    auth_patterns
    + profile_patterns
    + email_patterns
    + session_patterns
    + password_reset_patterns
    + email_change_patterns
)
