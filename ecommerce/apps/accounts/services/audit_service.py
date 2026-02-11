"""
Audit Logging Service

Handles all security-related event logging for the accounts app.
"""

import logging
from typing import Tuple, Optional
from django.http import HttpRequest
from apps.accounts.models import User
from apps.accounts import constants
from apps.accounts.utils import get_client_ip, get_user_agent

# Get security logger for file-based logging
security_logger = logging.getLogger("security")


class AuditService:
    """Service for managing audit logs"""

    @staticmethod
    def _log_event(
        action: str,
        user: Optional[User] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """
        Internal method to log audit events.

        File logging is synchronous (fast).
        Database writes are dispatched to Celery (non-blocking).
        """
        from apps.accounts.tasks import record_audit_log_task

        # Synchronous file-based logging (fast, no DB hit)
        user_email = user.email if user else "anonymous"
        security_logger.info(
            f"AUDIT: {action} | User: {user_email} | IP: {ip_address} | Metadata: {metadata}"
        )

        # Asynchronous DB write via Celery (non-blocking)
        record_audit_log_task.delay(
            user_id=str(user.id) if user else None,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
        )

    @staticmethod
    def _get_request_metadata(request: HttpRequest) -> Tuple[Optional[str], str]:
        """
        Extract IP address and user agent from request.

        Args:
            request: HTTP request object

        Returns:
            Tuple of (ip_address, user_agent)
        """
        return get_client_ip(request), get_user_agent(request)

    @staticmethod
    def log_login(user: User, request: HttpRequest) -> None:
        """
        Log successful login event.

        Args:
            user: User who logged in
            request: HTTP request object

        Returns:
            None
        """
        ip_address, user_agent = AuditService._get_request_metadata(request)
        AuditService._log_event(
            action=constants.AUDIT_ACTION_LOGIN,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def log_logout(user: User, request: HttpRequest) -> None:
        """Log logout"""
        ip_address, user_agent = AuditService._get_request_metadata(request)
        AuditService._log_event(
            action=constants.AUDIT_ACTION_LOGOUT,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def log_failed_login(
        email: str, request: HttpRequest, reason: Optional[str] = None
    ) -> None:
        """Log failed login attempt"""
        metadata = {"email": email}
        if reason:
            metadata["reason"] = reason

        ip_address, user_agent = AuditService._get_request_metadata(request)
        AuditService._log_event(
            action=constants.AUDIT_ACTION_FAILED_LOGIN,
            user=None,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
        )

    @staticmethod
    def log_password_change(
        user: User, request: HttpRequest, metadata: Optional[dict] = None
    ) -> None:
        """Log password change"""
        ip_address, user_agent = AuditService._get_request_metadata(request)
        AuditService._log_event(
            action=constants.AUDIT_ACTION_PASSWORD_CHANGE,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
        )

    @staticmethod
    def log_password_reset_request(
        user: User, ip_address: str = None, user_agent: str = None
    ) -> None:
        """Log password reset request"""
        AuditService._log_event(
            action="PASSWORD_RESET_REQUEST",
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def log_password_reset_complete(
        user: User, ip_address: str = None, user_agent: str = None
    ) -> None:
        """Log password reset completion"""
        AuditService._log_event(
            action="PASSWORD_RESET_COMPLETE",
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def log_email_verification(
        user: User, request: HttpRequest, metadata: Optional[dict] = None
    ) -> None:
        """Log email verification"""
        ip_address, user_agent = AuditService._get_request_metadata(request)
        AuditService._log_event(
            action=constants.AUDIT_ACTION_EMAIL_VERIFICATION,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
        )

    @staticmethod
    def log_email_change_request(
        user: User, new_email: str, ip_address: str = None, user_agent: str = None
    ) -> None:
        """Log email change request"""
        AuditService._log_event(
            action="EMAIL_CHANGE_REQUEST",
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"new_email": new_email, "current_email": user.email},
        )

    @staticmethod
    def log_email_change_complete(
        user: User,
        old_email: str,
        new_email: str,
        ip_address: str = None,
        user_agent: str = None,
    ) -> None:
        """Log email change completion - stores the history forever"""
        AuditService._log_event(
            action="EMAIL_CHANGE_COMPLETE",
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"from": old_email, "to": new_email},
        )

    @staticmethod
    def log_account_created(
        user: User, request: HttpRequest, metadata: Optional[dict] = None
    ) -> None:
        """Log account creation"""
        ip_address, user_agent = AuditService._get_request_metadata(request)
        AuditService._log_event(
            action=constants.AUDIT_ACTION_ACCOUNT_CREATED,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
        )

    @staticmethod
    def log_session_revoked(
        user: User,
        request: HttpRequest,
        session_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """Log session revocation"""
        meta = metadata or {}
        if session_id:
            meta["session_id"] = str(session_id)

        ip_address, user_agent = AuditService._get_request_metadata(request)
        AuditService._log_event(
            action=constants.AUDIT_ACTION_SESSION_REVOKED,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=meta,
        )

    @staticmethod
    def log_profile_update(
        user: User, request: HttpRequest, changes: Optional[dict] = None
    ) -> None:
        """Log profile update with what changed"""
        ip_address, user_agent = AuditService._get_request_metadata(request)
        AuditService._log_event(
            action="PROFILE_UPDATE",
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"changes": changes} if changes else {},
        )

    @staticmethod
    def log_account_deactivated(
        user: User, request: HttpRequest, reason: str = None
    ) -> None:
        """Log account deactivation"""
        ip_address, user_agent = AuditService._get_request_metadata(request)
        AuditService._log_event(
            action="ACCOUNT_DEACTIVATED",
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"reason": reason} if reason else {},
        )

    @staticmethod
    def log_account_reactivated(
        user: User, request: HttpRequest, reason: str = None
    ) -> None:
        """Log account reactivation"""
        ip_address, user_agent = AuditService._get_request_metadata(request)
        AuditService._log_event(
            action="ACCOUNT_REACTIVATED",
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"reason": reason} if reason else {},
        )
