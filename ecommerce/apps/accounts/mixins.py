"""
Reusable Mixins for Views

DRY principle: Extract common view logic into reusable mixins.
"""

from typing import Any
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.services import EmailService, AuditService
from apps.accounts import constants


class EmailVerificationMixin:
    """
    Mixin to automatically send verification email after user creation.

    Automatically called in create() method of CreateAPIView.
    """

    def send_verification_email(self, user) -> None:
        """
        Send verification email to user after transaction commits.

        Args:
            user: User instance to send email to
        """
        # Use on_commit to ensure email is only sent if DB transaction succeeds
        transaction.on_commit(lambda: EmailService.send_verification_email(user))


class AuditLoggingMixin:
    """
    Mixin to automatically log user creation in audit log.

    Requires self.request to be available.
    """

    def log_account_creation(self, user) -> None:
        """
        Log account creation in audit log.

        Args:
            user: User instance that was created
        """
        AuditService.log_account_created(user, self.request)


class RegistrationMixin(EmailVerificationMixin, AuditLoggingMixin):
    """
    Combined mixin for registration views.

    Handles:
    - Email verification sending (Atomic)
    - Audit logging (Atomic)
    - Standardized response format
    """

    def get_success_message(self, user) -> str:
        """
        Get success message for registration.

        Override in subclass to customize message.

        Args:
            user: Created user instance

        Returns:
            Success message string
        """
        return constants.CUSTOMER_REGISTRATION_SUCCESS.format(
            role=user.get_role_display()
        )

    def get_registration_response_data(self, user) -> dict:
        """
        Get response data for registration.

        Args:
            user: Created user instance

        Returns:
            Dictionary with response data
        """
        return {
            "message": self.get_success_message(user),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "role": user.role,
                "email_verified": user.email_verified,
            },
        }

    def perform_create(self, serializer) -> Any:
        """
        Override perform_create to add email verification and audit logging.

        Args:
            serializer: Validated serializer instance

        Returns:
            Created user instance
        """
        user = serializer.save()

        # Send verification email (scheduled for after commit)
        self.send_verification_email(user)

        # Log account creation
        self.log_account_creation(user)

        return user

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Override create to provide standardized response and atomicity.

        Args:
            request: HTTP request
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            HTTP Response with standardized format
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.perform_create(serializer)

        return Response(
            self.get_registration_response_data(user),
            status=status.HTTP_201_CREATED,
        )
