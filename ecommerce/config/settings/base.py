from pathlib import Path
from datetime import timedelta
import os
import environ

try:
    import sentry_sdk
except ImportError:
    sentry_sdk = None

# Initialize environment variables
env = environ.Env(DEBUG=(bool, False))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Adjust BASE_DIR for nested settings
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Read .env file if it exists
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Throttle rates from environment
THROTTLE_RATE_ANON = env("THROTTLE_RATE_ANON")
THROTTLE_RATE_USER = env("THROTTLE_RATE_USER")
THROTTLE_RATE_AUTH = env("THROTTLE_RATE_AUTH")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "phonenumber_field",
    # Local apps
    "apps.accounts",
    "apps.addresses",
    "apps.products",
    "apps.cart",
    "apps.orders",
    "apps.reviews",
]

AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "apps.core.middleware.RequestIDMiddleware",  # Add request ID to all requests
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "EXCEPTION_HANDLER": "config.exception_handlers.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": THROTTLE_RATE_ANON,  # For anonymous users
        "user": THROTTLE_RATE_USER,  # For authenticated users
        "auth": THROTTLE_RATE_AUTH,  # For auth endpoints (login, register)
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env.int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES")
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=env.int("JWT_REFRESH_TOKEN_LIFETIME_DAYS")
    ),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database defaults
DATABASES = {"default": env.db("DATABASE_URL")}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "apps.accounts.validators.EnhancedPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Media files
MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Email Configuration
EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

# Frontend URL
FRONTEND_URL = env("FRONTEND_URL")

# Phone Number Settings
PHONENUMBER_DEFAULT_REGION = "IN"
PHONENUMBER_DB_FORMAT = "E164"

# ============================================================================
# SENTRY ERROR TRACKING
# ============================================================================

SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
        send_default_pii=False,
        environment="production" if not DEBUG else "development",
    )

# ============================================================================
# CELERY CONFIGURATION
# ============================================================================

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")

# Task serialization
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# Timezone
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True

# Task tracking
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes max per task

# Beat schedule for periodic tasks
CELERY_BEAT_SCHEDULE = {
    "cleanup-expired-tokens": {
        "task": "apps.accounts.tasks.cleanup_expired_tokens",
        "schedule": 3600.0,  # Every hour
    },
    "cleanup-old-sessions": {
        "task": "apps.accounts.tasks.cleanup_old_sessions",
        "schedule": 86400.0,  # Every 24 hours
    },
}

# ============================================================================
# REDIS CACHE CONFIGURATION
# ============================================================================

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "ecommerce",
        "TIMEOUT": env("REDIS_TIMEOUT"),
    }
}

# Use Redis for session storage
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Logging Configuration
from .logging import LOGGING  # noqa: E402, F401

# =============================================================================
# SENTRY ERROR TRACKING (Optional)
# =============================================================================

if sentry_sdk:
    sentry_dsn = env("SENTRY_DSN", default="")

    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=env("ENVIRONMENT", default="development"),
            # Performance monitoring - sample 10% of transactions
            traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.1),
            # Profiling - sample 10% of transactions
            profiles_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.1),
            # Don't send personally identifiable information
            send_default_pii=False,
            # Don't send errors in DEBUG mode (development)
            before_send=lambda event, hint: event if not DEBUG else None,
            # Ignore common errors
            ignore_errors=[
                KeyboardInterrupt,
                "django.http.response.Http404",
            ],
        )
