"""
Password Reset and Email Change Views

API endpoints for password reset and email change flows.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.accounts.serializers.password_reset import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailChangeRequestSerializer,
    EmailChangeConfirmSerializer,
)
from apps.accounts.services.password_reset_service import (
    PasswordResetService,
    EmailChangeService,
)
from apps.accounts.views.auth import EmailThrottle
from apps.accounts.utils import get_client_ip, get_user_agent


class PasswordResetRequestView(APIView):
    """
    Request a password reset link.

    POST /api/v1/accounts/password-reset/
    {
        "email": "user@example.com"
    }

    Always returns 200 to prevent email enumeration.
    """

    permission_classes = [AllowAny]
    throttle_classes = [EmailThrottle]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get client info for security logging
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)

        success, message = PasswordResetService.request_password_reset(
            email=serializer.validated_data["email"],
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Always return success to prevent email enumeration
        return Response({"message": message}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with new password.

    POST /api/v1/accounts/password-reset/confirm/
    {
        "token": "uuid-token",
        "new_password": "newPassword123!",
        "confirm_password": "newPassword123!"
    }
    """

    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        success, message = PasswordResetService.confirm_password_reset(
            token_uuid=serializer.validated_data["token"],
            new_password=serializer.validated_data["new_password"],
        )

        if success:
            return Response({"message": message}, status=status.HTTP_200_OK)
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)


class EmailChangeRequestView(APIView):
    """
    Request an email change.

    POST /api/v1/accounts/email-change/
    {
        "new_email": "newemail@example.com",
        "password": "currentPassword123!"
    }

    Requires authentication and current password for security.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [EmailThrottle]
    serializer_class = EmailChangeRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        success, message = EmailChangeService.request_email_change(
            user=request.user,
            new_email=serializer.validated_data["new_email"],
        )

        if success:
            return Response({"message": message}, status=status.HTTP_200_OK)
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)


class EmailChangeConfirmView(APIView):
    """
    Confirm email change.

    POST /api/v1/accounts/email-change/confirm/
    {
        "token": "uuid-token"
    }
    """

    permission_classes = [AllowAny]  # Link in email, user might not be logged in
    serializer_class = EmailChangeConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        success, message = EmailChangeService.confirm_email_change(
            token_uuid=serializer.validated_data["token"],
        )

        if success:
            return Response({"message": message}, status=status.HTTP_200_OK)
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
