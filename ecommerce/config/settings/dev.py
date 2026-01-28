from .base import *  # noqa: F403


# Enable debug mode for development - allows static file serving
DEBUG = True

ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True

# Email Configuration for Development
# Prints emails to console instead of actually sending them
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@ecommerce.com"

# Frontend URL for email verification links (for local dev)
FRONTEND_URL = "http://localhost:3000"

# For local development, we can use a simpler logging or additional apps
# INSTALLED_APPS += [
#     # "debug_toolbar",
# ]

# Database for development
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }
