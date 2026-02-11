"""
Celery Tasks for Accounts App

Background tasks for email sending and cleanup operations.
All tasks are idempotent and use retry strategies for reliability.
"""

import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger("celery.tasks")


# ============================================================================
# EMAIL TASKS
# ============================================================================


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=5,
)
def send_verification_email_task(self, user_id):
    """
    Send email verification link to user.

    Args:
        user_id: UUID of the user

    This task is idempotent - safe to retry.
    """
    from apps.accounts.models import User
    from apps.accounts.services.email_service import EmailService

    try:
        user = User.objects.get(id=user_id)

        # Idempotency check
        if user.email_verified:
            logger.info(f"Email already verified for user {user_id}")
            return "Email already verified"

        EmailService.send_verification_email(user)
        logger.info(f"Verification email sent to user {user_id}")
        return f"Verification email sent to {user.email}"

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=5,
)
def send_password_reset_email_task(self, user_id, reset_url, expiry_hours):
    """
    Send password reset email to user.

    Args:
        user_id: UUID of the user
        reset_url: Password reset URL with token
        expiry_hours: Token expiry time in hours
    """
    from apps.accounts.models import User
    from apps.accounts.services.email_service import EmailService

    try:
        user = User.objects.get(id=user_id)
        EmailService.send_password_reset_email(user, reset_url, expiry_hours)
        logger.info(f"Password reset email sent to user {user_id}")
        return f"Password reset email sent to {user.email}"

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=5,
)
def send_email_change_email_task(self, new_email, verification_url, expiry_hours):
    """
    Send email change verification to new email address.

    Args:
        new_email: New email address
        verification_url: Verification URL with token
        expiry_hours: Token expiry time in hours
    """
    from apps.accounts.services.email_service import EmailService

    EmailService.send_email_change_email(new_email, verification_url, expiry_hours)
    logger.info(f"Email change verification sent to {new_email}")
    return f"Email change verification sent to {new_email}"


# ============================================================================
# AUDIT LOGGING TASK (Async DB writes)
# ============================================================================


@shared_task(name="accounts.record_audit_log", bind=True, max_retries=3)
def record_audit_log_task(self, user_id, action, ip_address, user_agent, metadata):
    """
    Write audit log to DB in background (non-blocking).

    This task is called by AuditService to prevent blocking the request thread
    with database writes. File logging remains synchronous for speed.

    Args:
        user_id: UUID string of the user (or None for anonymous)
        action: Audit action constant
        ip_address: Client IP address
        user_agent: Client user agent string
        metadata: Additional metadata dict
    """
    from apps.accounts.models import AuditLog

    try:
        AuditLog.objects.create(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
        )
        logger.info(f"Audit log recorded: {action} for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to record audit log: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60)


# ============================================================================
# CLEANUP TASKS (Scheduled via Celery Beat)
# ============================================================================


@shared_task(name="apps.accounts.tasks.cleanup_expired_tokens")
def cleanup_expired_tokens():
    """
    Periodic task to clean up expired tokens.

    Removes:
    - Expired email verification tokens
    - Expired password reset tokens
    - Expired email change tokens

    Runs hourly via Celery Beat.
    """
    from apps.accounts.models import (
        EmailVerificationToken,
        PasswordResetToken,
        EmailChangeToken,
    )

    now = timezone.now()

    # Clean up email verification tokens
    email_tokens_deleted = EmailVerificationToken.objects.filter(
        created_at__lt=now - timedelta(hours=24),
        is_used=False,
    ).delete()[0]

    # Clean up password reset tokens
    password_tokens_deleted = PasswordResetToken.objects.filter(
        created_at__lt=now - timedelta(hours=24),
        is_used=False,
    ).delete()[0]

    # Clean up email change tokens
    email_change_tokens_deleted = EmailChangeToken.objects.filter(
        created_at__lt=now - timedelta(hours=24),
        is_used=False,
    ).delete()[0]

    total_deleted = (
        email_tokens_deleted + password_tokens_deleted + email_change_tokens_deleted
    )

    logger.info(
        f"Cleanup completed: {total_deleted} expired tokens deleted "
        f"(email: {email_tokens_deleted}, password: {password_tokens_deleted}, "
        f"email_change: {email_change_tokens_deleted})"
    )

    return f"Deleted {total_deleted} expired tokens"


@shared_task(name="apps.accounts.tasks.cleanup_old_sessions")
def cleanup_old_sessions():
    """
    Periodic task to clean up old user sessions.

    Removes sessions older than 30 days.
    Runs daily via Celery Beat.
    """
    from apps.accounts.models import UserSession

    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count = UserSession.objects.filter(last_activity__lt=cutoff_date).delete()[
        0
    ]

    logger.info(f"Cleanup completed: {deleted_count} old sessions deleted")
    return f"Deleted {deleted_count} old sessions"
