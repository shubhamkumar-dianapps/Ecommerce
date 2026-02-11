"""
Celery Configuration for E-commerce Backend

This module initializes the Celery application and configures it to work with Django.
Tasks are auto-discovered from all installed apps.
"""

import os
import logging
from celery import Celery
from celery.signals import (
    task_prerun,
    task_postrun,
    task_failure,
    task_retry,
    task_success,
    setup_logging,
)

# Set default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

# Initialize Django
import django

django.setup()

# Create Celery app
app = Celery("ecommerce")

# Load configuration from Django settings with CELERY_ namespace
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()

# Task-level configuration for reliability
app.conf.task_acks_late = True  # Re-queue tasks if worker crashes
app.conf.worker_prefetch_multiplier = 1  # Fair task distribution across workers

# Get logger for Celery operations
celery_logger = logging.getLogger("celery")


# ============================================================================
# LOGGING INTEGRATION
# ============================================================================


@setup_logging.connect
def config_loggers(*args, **kwargs):
    """
    Configure Celery logging to use Django's LOGGING configuration.
    This ensures Celery logs go to our file handlers as defined in base.py.
    """
    from django.conf import settings
    from logging.config import dictConfig

    dictConfig(settings.LOGGING)


# ============================================================================
# CELERY SIGNAL HANDLERS FOR LOGGING
# ============================================================================


@task_prerun.connect
def log_task_start(
    sender=None, task_id=None, task=None, args=None, kwargs=None, **extra
):
    """Log when a task starts execution."""
    celery_logger.info(
        f"Task started: {task.name} | ID: {task_id} | Args: {args} | Kwargs: {kwargs}"
    )


@task_success.connect
def log_task_success(sender=None, result=None, **extra):
    """Log when a task completes successfully."""
    celery_logger.info(f"Task succeeded: {sender.name} | Result: {result}")


@task_failure.connect
def log_task_failure(
    sender=None, task_id=None, exception=None, traceback=None, **extra
):
    """Log when a task fails."""
    celery_logger.error(
        f"Task failed: {sender.name} | ID: {task_id} | Exception: {exception}",
        exc_info=True,
    )


@task_retry.connect
def log_task_retry(sender=None, task_id=None, reason=None, einfo=None, **extra):
    """Log when a task is retried."""
    celery_logger.warning(
        f"Task retry: {sender.name} | ID: {task_id} | Reason: {reason}"
    )


@task_postrun.connect
def log_task_complete(
    sender=None, task_id=None, task=None, retval=None, state=None, **extra
):
    """Log when a task completes (regardless of success/failure)."""
    celery_logger.info(f"Task completed: {task.name} | ID: {task_id} | State: {state}")


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to verify Celery is working correctly."""
    celery_logger.info(f"Debug task executed: {self.request!r}")
