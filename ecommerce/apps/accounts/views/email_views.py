from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from apps.accounts.serializers.email_verification import (
    EmailVerificationSerializer,
    ResendVerificationSerializer,
)
from apps.accounts.services import EmailService, AuditService
from apps.accounts.models import User


class VerifyEmailView(APIView):
    """View to verify email using token"""

    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        success, message, user = EmailService.verify_email(token)

        if success:
            # Log verification event
            AuditService.log_email_verification(user, request)
            return Response(
                {"message": message, "email": user.email},
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationEmailView(APIView):
    """View to resend verification email"""

    permission_classes = [AllowAny]
    serializer_class = ResendVerificationSerializer

    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email.lower())
            success, message = EmailService.resend_verification_email(user)

            if success:
                return Response({"message": message}, status=status.HTTP_200_OK)
            else:
                return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            return Response(
                {"message": "If the email exists, a verification link has been sent"},
                status=status.HTTP_200_OK,
            )
