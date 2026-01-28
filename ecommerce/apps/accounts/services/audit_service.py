"""
Audit Logging Service

Handles all security-related event logging for the accounts app.
"""

from typing import Tuple, Optional
from django.http import HttpRequest
from apps.accounts.models import AuditLog, User
from apps.accounts import constants
from apps.accounts.utils import get_client_ip, get_user_agent


class AuditService:
    """Service for managing audit logs"""

    @staticmethod
    def _log_event(
        action: str,
        user: Optional[User] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> AuditLog:
        """Internal method to create audit log entry"""
        return AuditLog.objects.create(
            user=user,
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
    def log_login(user: User, request: HttpRequest) -> AuditLog:
        """
        Log successful login event.

        Args:
            user: User who logged in
            request: HTTP request object

        Returns:
            Created AuditLog instance
        """
        ip_address, user_agent = AuditService._get_request_metadata(request)
        return AuditService._log_event(
            action=constants.AUDIT_ACTION_LOGIN,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def log_logout(user: User, request: HttpRequest) -> AuditLog:
        """Log logout"""
        ip_address, user_agent = AuditService._get_request_metadata(request)
        return AuditService._log_event(
            action=constants.AUDIT_ACTION_LOGOUT,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def log_failed_login(
        email: str, request: HttpRequest, reason: Optional[str] = None
    ) -> AuditLog:
        """Log failed login attempt"""
        metadata = {"email": email}
        if reason:
            metadata["reason"] = reason

        ip_address, user_agent = AuditService._get_request_metadata(request)
        return AuditService._log_event(
            action=constants.AUDIT_ACTION_FAILED_LOGIN,
            user=None,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
        )

    @staticmethod
    def log_password_change(
        user: User, request: HttpRequest, metadata: Optional[dict] = None
    ) -> AuditLog:
        """Log password change"""
        ip_address, user_agent = AuditService._get_request_metadata(request)
        return AuditService._log_event(
            action=constants.AUDIT_ACTION_PASSWORD_CHANGE,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
        )

    @staticmethod
    def log_password_reset_request(
        user: User, request: HttpRequest, metadata: Optional[dict] = None
    ) -> AuditLog:
        """Log password reset request"""
        ip_address, user_agent = AuditService._get_request_metadata(request)
        return AuditService._log_event(
            action="PASSWORD_RESET_REQUEST",
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
        )

    @staticmethod
    def log_email_verification(
        user: User, request: HttpRequest, metadata: Optional[dict] = None
    ) -> AuditLog:
        """Log email verification"""
        ip_address, user_agent = AuditService._get_request_metadata(request)
        return AuditService._log_event(
            action=constants.AUDIT_ACTION_EMAIL_VERIFICATION,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
        )

    @staticmethod
    def log_account_created(
        user: User, request: HttpRequest, metadata: Optional[dict] = None
    ) -> AuditLog:
        """Log account creation"""
        ip_address, user_agent = AuditService._get_request_metadata(request)
        return AuditService._log_event(
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
    ) -> AuditLog:
        """Log session revocation"""
        meta = metadata or {}
        if session_id:
            meta["session_id"] = str(session_id)

        ip_address, user_agent = AuditService._get_request_metadata(request)
        return AuditService._log_event(
            action=constants.AUDIT_ACTION_SESSION_REVOKED,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=meta,
        )

    @staticmethod
    def log_profile_update(
        user: User, request: HttpRequest, metadata: Optional[dict] = None
    ) -> AuditLog:
        """Log profile update"""
        ip_address, user_agent = AuditService._get_request_metadata(request)
        return AuditService._log_event(
            action="PROFILE_UPDATE",
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
        )
