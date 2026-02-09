from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from apps.accounts.models import EmailVerificationToken, User
from apps.accounts import constants


class EmailService:
    """Service for handling email verification"""

    @staticmethod
    def send_verification_email(user):
        """
        Create a verification token and send verification email to user.
        Returns the created token.
        """
        # Create verification token
        token = EmailVerificationToken.objects.create(user=user)

        # Build verification URL (customize based on your frontend)
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{token.token}"

        # Build email from template
        subject = constants.EMAIL_SUBJECT_VERIFICATION
        message = constants.EMAIL_VERIFICATION_TEMPLATE.format(
            email=user.email,
            verification_url=verification_url,
            expiry_hours=constants.EMAIL_VERIFICATION_EXPIRY_HOURS,
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return token

    @staticmethod
    @transaction.atomic
    def verify_email(token_value):
        """
        Verify email using token.
        Returns (success: bool, message: str, user: User|None)
        """
        try:
            # Lock the token row
            token = EmailVerificationToken.objects.select_for_update().get(
                token=token_value
            )

            if not token.is_valid():
                if token.is_used:
                    return False, "This verification link has already been used", None
                else:
                    return False, "This verification link has expired", None

            # Mark token as used
            token.mark_as_used()

            # Mark user email as verified with database-level locking
            user = User.objects.select_for_update().get(pk=token.user_id)
            user.email_verified = True
            user.save(update_fields=["email_verified"])

            return True, "Email verified successfully", user

        except EmailVerificationToken.DoesNotExist:
            return False, "Invalid verification link", None

    @staticmethod
    def resend_verification_email(user):
        """
        Resend verification email.
        Invalidates old tokens and creates a new one.
        """
        if user.email_verified:
            return False, "Email is already verified"

        # Delete old unused tokens
        EmailVerificationToken.objects.filter(user=user, is_used=False).delete()

        # Send new verification email
        EmailService.send_verification_email(user)

        return True, "Verification email sent"

    @staticmethod
    def send_password_reset_email(user, reset_url, expiry_hours):
        """Send password reset email"""
        subject = constants.EMAIL_PASSWORD_RESET_SUBJECT
        message = constants.EMAIL_PASSWORD_RESET_TEMPLATE.format(
            email=user.email,
            reset_url=reset_url,
            expiry_hours=expiry_hours,
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

    @staticmethod
    def send_email_change_email(new_email, verification_url, expiry_hours):
        """Send email change verification email to the NEW address"""
        subject = constants.EMAIL_CHANGE_SUBJECT
        message = constants.EMAIL_CHANGE_TEMPLATE.format(
            new_email=new_email,
            verification_url=verification_url,
            expiry_hours=expiry_hours,
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [new_email],
            fail_silently=False,
        )
