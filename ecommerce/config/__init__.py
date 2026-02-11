"""
Config package initialization.

Import Celery app so Django auto-discovers it on startup.
This ensures task auto-discovery and signal handlers work correctly.
"""

from .celery import app as celery_app

__all__ = ("celery_app",)
