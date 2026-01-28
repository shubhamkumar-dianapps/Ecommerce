from .base import *  # noqa: F403, F405


DEBUG = False

# SECURITY: Set this to your production domain
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

# Use more secure DB engine in production like PostgreSQL
DATABASES = {"default": env.db("DATABASE_URL")}

# Production security headers
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
