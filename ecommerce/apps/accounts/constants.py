"""
Accounts App Constants

All magic numbers, strings, and configuration values for the accounts app.
NEVER use hard-coded values in models, serializers, or views.
"""

# Field Length Constants
NAME_MAX_LENGTH = 255
DEPARTMENT_MAX_LENGTH = 100
GST_NUMBER_LENGTH = 15
ROLE_MAX_LENGTH = 20
SESSION_KEY_MAX_LENGTH = 255
PROVIDER_MAX_LENGTH = 50
ACTION_MAX_LENGTH = 50
UID_MAX_LENGTH = 255

# Email Verification
EMAIL_VERIFICATION_EXPIRY_HOURS = 24
EMAIL_SUBJECT_VERIFICATION = "Verify your email address"
EMAIL_VERIFICATION_SUCCESS = "Email verified successfully"
EMAIL_ALREADY_VERIFIED = "Email is already verified"
EMAIL_VERIFICATION_SENT = "Verification email sent"
EMAIL_LINK_EXPIRED = "This verification link has expired"
EMAIL_LINK_USED = "This verification link has already been used"
EMAIL_LINK_INVALID = "Invalid verification link"

# Email Templates
# Use {variable} for placeholders that will be replaced with .format()
EMAIL_VERIFICATION_TEMPLATE = """
Hi {email},

Please click the link below to verify your email address:
{verification_url}

This link will expire in {expiry_hours} hours.

If you didn't create an account, please ignore this email.

Thanks,
The E-commerce Team
"""

# TODO: Implement password reset flow using these constants
EMAIL_PASSWORD_RESET_SUBJECT = "Reset your password"
EMAIL_PASSWORD_RESET_TEMPLATE = """
Hi {email},

You requested to reset your password. Click the link below:
{reset_url}

This link will expire in {expiry_hours} hours.

If you didn't request this, please ignore this email.

Thanks,
The E-commerce Team
"""

# Email Change
EMAIL_CHANGE_SUBJECT = "Verify your new email address"
EMAIL_CHANGE_TEMPLATE = """
Hi,

You requested to change your email address to {new_email}.

Please click the link below to confirm this change:
{verification_url}

This link will expire in {expiry_hours} hours.

If you didn't request this change, please ignore this email and your email will remain unchanged.

Thanks,
The E-commerce Team
"""

# TODO: Implement welcome email flow using these constants
EMAIL_WELCOME_SUBJECT = "Welcome to E-commerce!"
EMAIL_WELCOME_TEMPLATE = """
Hi {email},

Welcome to our platform! Your {role} account has been created successfully.

{additional_message}

Thanks,
The E-commerce Team
"""

# Registration Messages
CUSTOMER_REGISTRATION_SUCCESS = "{role} account created successfully. Please check your email to verify your account."
SHOPKEEPER_VERIFICATION_NOTICE = (
    " Your shop will be verified by our team within 24-48 hours."
)
SHOPKEEPER_PENDING_VERIFICATION_WARNING = (
    "Your shop is pending verification. Some features may be limited."
)
ADMIN_REGISTRATION_FORBIDDEN = (
    "Admin accounts cannot be created via API. Contact support."
)

# Password
PASSWORD_MISMATCH_ERROR = "Passwords do not match"
PASSWORD_HELP_TEXT = "Password must meet complexity requirements"
PASSWORD_CONFIRM_HELP_TEXT = "Must match password"

# GST
GST_LENGTH_ERROR = "GST number must be exactly {length} characters"
GST_HELP_TEXT = "GST registration number ({length} characters)"

# Phone
PHONE_HELP_TEXT = "Phone number in international format (e.g., +919876543210)"

# Session
SESSION_REVOKED_SUCCESS = "Session invalidated successfully"
SESSION_NOT_FOUND = "Session not found or already inactive"
SESSIONS_REVOKED_COUNT = "{count} session(s) revoked successfully"

# API Messages
LEGACY_ENDPOINT_WARNING = (
    "This endpoint is deprecated. Use role-specific registration endpoints."
)

# Pagination
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
AUDIT_LOG_PAGE_SIZE = 20
SESSION_PAGE_SIZE = 10

# Session Configuration (can be overridden in .env)
DEFAULT_SESSION_EXPIRY_DAYS = 30
DEFAULT_MAX_ACTIVE_SESSIONS_PER_USER = 5

# Admin
ADMIN_LIST_PER_PAGE = 25

# Audit Log Actions
# (These match the AuditLog.Action choices)
AUDIT_ACTION_LOGIN = "LOGIN"
AUDIT_ACTION_LOGOUT = "LOGOUT"
AUDIT_ACTION_FAILED_LOGIN = "FAILED_LOGIN"
AUDIT_ACTION_PASSWORD_CHANGE = "PASSWORD_CHANGE"
AUDIT_ACTION_EMAIL_VERIFICATION = "EMAIL_VERIFICATION"
AUDIT_ACTION_ACCOUNT_CREATED = "ACCOUNT_CREATED"
AUDIT_ACTION_SESSION_REVOKED = "SESSION_REVOKED"

# Authentication

AUTH_RATE = "5/m"
AUTH_RATE_MESSAGE = "Too many authentication attempts. Please try again in a minute."
EMAIL_RATE = (
    "3/h"  # Strict limit for email-sending endpoints (password reset, email change)
)
EMAIL_RATE_MESSAGE = "Too many email requests. Please try again later."
MAX_ACTIVE_SESSIONS_PER_USER = 5
MAX_ACTIVE_SESSIONS_EXCEEDED = (
    "Maximum active sessions limit reached. Please logout from another device first."
)
