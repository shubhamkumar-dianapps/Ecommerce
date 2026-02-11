"""
Logging Configuration

Comprehensive file-based logging with different log files for different types.
Console logging is enabled only in DEBUG mode.
"""

import os
from pathlib import Path

# Base directory for logs
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"

# Create logs directory if it doesn't exist
os.makedirs(LOGS_DIR, exist_ok=True)

# Determine if we're in DEBUG mode (will be set by settings/base.py)
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    # Formatters define how log messages look
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} [{request_id}] {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} [{request_id}] {message}",
            "style": "{",
        },
        "security": {
            "format": "[{asctime}] {levelname} | {name} | [{request_id}] | {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "request": {
            "format": "[{asctime}] {levelname} {status_code} {request.method} {request.path} [{request_id}]",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    # Filters add contextual information to log records
    "filters": {
        "request_id": {
            "()": "apps.core.logging_filters.RequestIDFilter",
        },
    },
    # Handlers define where logs go
    "handlers": {
        # Console output (for development only)
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        # General application logs
        "file_general": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOGS_DIR / "general.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
            "filters": ["request_id"],
            "encoding": "utf-8",
        },
        # Error logs (WARNING and above)
        "file_error": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOGS_DIR / "error.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 10,
            "formatter": "verbose",
            "filters": ["request_id"],
            "encoding": "utf-8",
        },
        # Security/Audit logs (logins, password changes, etc.)
        "file_security": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOGS_DIR / "security.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 30,  # Keep more security logs
            "formatter": "security",
            "filters": ["request_id"],
            "encoding": "utf-8",
        },
        # Database/SQL logs
        "file_database": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOGS_DIR / "database.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 3,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        # API Request logs
        "file_api": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOGS_DIR / "api.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
            "filters": ["request_id"],
            "encoding": "utf-8",
        },
        # Payment/Transaction logs (critical, keep longer)
        "file_payment": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOGS_DIR / "payment.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 50,  # Keep payment logs for a long time
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        # Redis cache logs
        "file_redis": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOGS_DIR / "redis.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 10,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        # Celery task logs
        "file_celery": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOGS_DIR / "celery.log"),
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 10,
            "formatter": "verbose",
            "encoding": "utf-8",
        },
    },
    # Loggers define which handlers are used for which modules
    "loggers": {
        # Root logger - catches everything
        "": {
            "handlers": ["file_general", "file_error"] + (["console"] if DEBUG else []),
            "level": "INFO",
        },
        # Django framework logs
        "django": {
            "handlers": ["file_general"] + (["console"] if DEBUG else []),
            "level": "INFO",
            "propagate": False,
        },
        # Django request logs (404s, 500s, etc.)
        "django.request": {
            "handlers": ["file_error", "file_api"],
            "level": "WARNING",
            "propagate": False,
        },
        # Django security logs
        "django.security": {
            "handlers": ["file_security", "file_error"],
            "level": "WARNING",
            "propagate": False,
        },
        # Database query logs (set to DEBUG to log all SQL)
        "django.db.backends": {
            "handlers": ["file_database"],
            "level": "DEBUG"
            if os.environ.get("LOG_SQL", "False").lower() in ("true", "1", "yes")
            else "WARNING",
            "propagate": False,
        },
        # Our custom security logger (used by AuditService)
        "security": {
            "handlers": ["file_security"] + (["console"] if DEBUG else []),
            "level": "INFO",
            "propagate": False,
        },
        # API logger for REST framework
        "api": {
            "handlers": ["file_api"] + (["console"] if DEBUG else []),
            "level": "INFO",
            "propagate": False,
        },
        # Payment/Order logger
        "payment": {
            "handlers": ["file_payment", "file_security"],
            "level": "INFO",
            "propagate": False,
        },
        # Accounts app logger
        "apps.accounts": {
            "handlers": ["file_general", "file_security"],
            "level": "INFO",
            "propagate": False,
        },
        # Orders app logger
        "apps.orders": {
            "handlers": ["file_general", "file_payment"],
            "level": "INFO",
            "propagate": False,
        },
        # Cart app logger
        "apps.cart": {
            "handlers": ["file_general"],
            "level": "INFO",
            "propagate": False,
        },
        # Products app logger
        "apps.products": {
            "handlers": ["file_general"],
            "level": "INFO",
            "propagate": False,
        },
        # Redis cache logger
        "redis": {
            "handlers": ["file_redis"],
            "level": "INFO",
            "propagate": False,
        },
        # Celery tasks logger
        "celery": {
            "handlers": ["file_celery"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
