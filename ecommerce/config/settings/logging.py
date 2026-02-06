"""
Logging Configuration

Comprehensive file-based logging with different log files for different types.
"""

import os
from pathlib import Path

# Base directory for logs
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"

# Create logs directory if it doesn't exist
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    # Formatters define how log messages look
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
        "security": {
            "format": "[{asctime}] {levelname} | {name} | {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "request": {
            "format": "[{asctime}] {levelname} {status_code} {request.method} {request.path}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    # Handlers define where logs go
    "handlers": {
        # Console output (for development)
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
    },
    # Loggers define which handlers are used for which modules
    "loggers": {
        # Root logger - catches everything
        "": {
            "handlers": ["console", "file_general", "file_error"],
            "level": "INFO",
        },
        # Django framework logs
        "django": {
            "handlers": ["console", "file_general"],
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
            "level": "WARNING",  # Set to DEBUG to log all queries
            "propagate": False,
        },
        # Our custom security logger (used by AuditService)
        "security": {
            "handlers": ["file_security", "console"],
            "level": "INFO",
            "propagate": False,
        },
        # API logger for REST framework
        "api": {
            "handlers": ["file_api", "console"],
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
    },
}
