from .base import *  # noqa: F403


DEBUG = False

ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True

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
