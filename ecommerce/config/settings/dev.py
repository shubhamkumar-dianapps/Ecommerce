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

# =============================================================================
# Django Silk - SQL Query & Performance Profiling (Optional)
# Access at: http://127.0.0.1:8000/silk/
# Install with: pip install django-silk
# =============================================================================
try:
    import silk  # noqa: F401

    INSTALLED_APPS += [  # noqa: F405
        "silk",
    ]
    MIDDLEWARE.insert(0, "silk.middleware.SilkyMiddleware")  # noqa: F405

    # Silk Configuration
    SILKY_PYTHON_PROFILER = False  # Disable Python profiler (causes file issues)
    SILKY_PYTHON_PROFILER_BINARY = False  # Disable binary profiling
    SILKY_META = True  # Show Silk's own overhead
    SILKY_MAX_REQUEST_BODY_SIZE = 1024  # Max request body size to log (KB)
    SILKY_MAX_RESPONSE_BODY_SIZE = 1024  # Max response body size to log (KB)
    SILKY_INTERCEPT_PERCENT = 100  # Profile 100% of requests
    SILKY_MAX_RECORDED_REQUESTS = 10000  # Max requests to store
    SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 10  # Check limit every 10%
except ImportError:
    pass  # Silk not installed, skip profiling

# Database for development
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }
