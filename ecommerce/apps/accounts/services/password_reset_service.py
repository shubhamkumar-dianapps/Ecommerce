"""
Password Reset and Email Change Services

Business logic for password reset and email change flows.
"""

import logging
from typing import Tuple
from django.conf import settings
from django.db import transaction
from apps.accounts.models import User, PasswordResetToken, EmailChangeToken
from apps.accounts.services.audit_service import AuditService
from apps.accounts.services.email_service import EmailService

# Get security logger
security_logger = logging.getLogger("security")


class PasswordResetService:
    """Service for password reset operations."""

    @staticmethod
    def request_password_reset(
        email: str, ip_address: str = None, user_agent: str = ""
    ) -> Tuple[bool, str]:
        """
        Request a password reset.

        Creates a token and sends email if user exists.
        Always returns success to prevent email enumeration.

        Args:
            email: User's email address
            ip_address: Requester's IP address
            user_agent: Requester's user agent

        Returns:
            Tuple of (success, message)
        """
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            # Log attempt for non-existent user (security monitoring)
            security_logger.warning(
                f"Password reset attempted for non-existent email: {email} | IP: {ip_address}"
            )
            # Return success to prevent email enumeration
            return True, "If an account exists, a reset link has been sent"

        # Invalidate any existing unused tokens
        PasswordResetToken.objects.filter(user=user, is_used=False).delete()

        # Create new token
        token = PasswordResetToken.objects.create(
            user=user,
        )

        # Log the password reset request
        AuditService.log_password_reset_request(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Build reset URL
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{token.token}"

        # Send email using centralized service
        EmailService.send_password_reset_email(
            user=user,
            reset_url=reset_url,
            expiry_hours=PasswordResetToken.EXPIRY_HOURS,
        )

        return True, "If an account exists, a reset link has been sent"

    @staticmethod
    @transaction.atomic
    def confirm_password_reset(token_uuid: str, new_password: str) -> Tuple[bool, str]:
        """
        Confirm password reset with new password.

        Args:
            token_uuid: The reset token UUID
            new_password: The new password

        Returns:
            Tuple of (success, message)
        """
        try:
            token = PasswordResetToken.objects.select_for_update().get(token=token_uuid)
        except PasswordResetToken.DoesNotExist:
            security_logger.warning(
                f"Invalid password reset token attempted: {token_uuid}"
            )
            return False, "Invalid or expired reset link"

        if not token.is_valid():
            security_logger.warning(
                f"Expired/used password reset token attempted: {token_uuid} | User: {token.user.email}"
            )
            return False, "This reset link has expired or already been used"

        # Update password with database-level locking on User
        user = User.objects.select_for_update().get(pk=token.user_id)
        user.set_password(new_password)
        user.save(update_fields=["password"])

        # Mark token as used
        token.mark_as_used()

        # Log the successful password reset (context will be captured by AuditService)
        # We don't need to pass IP/UA here if we want current context,
        # but for accuracy we'll let AuditService handle it via request or defaults.
        AuditService.log_password_reset_complete(
            user=user,
        )

        security_logger.info(f"Password reset completed for user: {user.email}")
        return True, "Password has been reset successfully"


class EmailChangeService:
    """Service for email change operations."""

    @staticmethod
    def request_email_change(
        user: User, new_email: str, ip_address: str = None, user_agent: str = ""
    ) -> Tuple[bool, str]:
        """
        Request an email change.

        Creates a token and sends verification email to the new address.

        Args:
            user: The user requesting the change
            new_email: The new email address
            ip_address: Requester's IP address
            user_agent: Requester's user agent

        Returns:
            Tuple of (success, message)
        """
        # Check if new email is already in use
        if User.objects.filter(email=new_email).exists():
            return False, "This email is already in use"

        # Invalidate any existing unused tokens
        EmailChangeToken.objects.filter(user=user, is_used=False).delete()

        # Create new token
        token = EmailChangeToken.objects.create(
            user=user,
            new_email=new_email,
        )

        # Log the email change request
        AuditService.log_email_change_request(
            user=user,
            new_email=new_email,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Build verification URL
        verification_url = f"{settings.FRONTEND_URL}/verify-email-change/{token.token}"

        # Send email to NEW address using centralized service
        EmailService.send_email_change_email(
            new_email=new_email,
            verification_url=verification_url,
            expiry_hours=EmailChangeToken.EXPIRY_HOURS,
        )

        return True, f"Verification email sent to {new_email}"

    @staticmethod
    @transaction.atomic
    def confirm_email_change(token_uuid: str) -> Tuple[bool, str]:
        """
        Confirm email change.

        Args:
            token_uuid: The verification token UUID

        Returns:
            Tuple of (success, message)
        """
        try:
            token = EmailChangeToken.objects.select_for_update().get(token=token_uuid)
        except EmailChangeToken.DoesNotExist:
            security_logger.warning(
                f"Invalid email change token attempted: {token_uuid}"
            )
            return False, "Invalid or expired verification link"

        if not token.is_valid():
            security_logger.warning(
                f"Expired/used email change token attempted: {token_uuid} | User: {token.user.email}"
            )
            return False, "This verification link has expired or already been used"

        # Check if new email is still available
        if User.objects.filter(email=token.new_email).exists():
            return False, "This email is already in use by another account"

        # Update user's email with database-level locking
        user = User.objects.select_for_update().get(pk=token.user_id)
        old_email = user.email
        user.email = token.new_email
        user.save(update_fields=["email"])

        # Mark token as used
        token.mark_as_used()

        # Log the successful email change (THIS IS THE PERMANENT HISTORY!)
        AuditService.log_email_change_complete(
            user=user,
            old_email=old_email,
            new_email=token.new_email,
        )

        security_logger.info(
            f"Email change completed: {old_email} -> {token.new_email} | User ID: {user.id}"
        )
        return True, f"Email changed successfully from {old_email} to {token.new_email}"
