"""
Authentication Views for Accounts App

Handles user registration and login with proper separation by role.
Uses mixins for DRY principles and follows REST best practices.
"""

from typing import Dict, Any
from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.serializers.register import (
    CustomerRegistrationSerializer,
    ShopkeeperRegistrationSerializer,
    LegacyRegisterSerializer,
)
from apps.accounts.serializers.login import LoginSerializer
from apps.accounts.services import AuthService, AuditService
from apps.accounts.mixins import RegistrationMixin
from apps.accounts import constants


class AuthThrottle(AnonRateThrottle):
    """Custom throttle for auth endpoints to prevent brute force attacks"""

    rate = constants.AUTH_RATE
    scope = "auth"


class CustomerRegistrationView(RegistrationMixin, generics.CreateAPIView):
    """
    Customer Registration Endpoint

    POST /api/v1/accounts/register/customer/

    Registers a new customer account with email verification.
    Required fields: email, phone, password, password_confirm, full_name
    """

    serializer_class = CustomerRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]


class ShopkeeperRegistrationView(RegistrationMixin, generics.CreateAPIView):
    """
    Shopkeeper Registration Endpoint

    POST /api/v1/accounts/register/shopkeeper/

    Registers a new shopkeeper account (requires admin verification).
    Required fields: email, phone, password, password_confirm, shop_name, gst_number

    Note: Shopkeeper accounts require manual verification by admin before they can operate.
    """

    serializer_class = ShopkeeperRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def get_success_message(self, user) -> str:
        """Override to add shopkeeper verification notice"""
        base_message = super().get_success_message(user)
        return base_message + constants.SHOPKEEPER_VERIFICATION_NOTICE


class LegacyRegisterView(RegistrationMixin, generics.CreateAPIView):
    """
    DEPRECATED: Legacy Registration Endpoint

    POST /api/v1/accounts/register/

    This endpoint is deprecated and will be removed in future versions.
    Please use:
    - /api/v1/accounts/register/customer/ for customer registration
    - /api/v1/accounts/register/shopkeeper/ for shopkeeper registration

    Note: Admin registration is not allowed via API.
    """

    serializer_class = LegacyRegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def get_registration_response_data(self, user) -> Dict[str, Any]:
        """Override to add deprecation warning"""
        data = super().get_registration_response_data(user)
        data["warning"] = constants.LEGACY_ENDPOINT_WARNING
        return data


class LoginView(TokenObtainPairView):
    """
    User Login Endpoint

    POST /api/v1/accounts/login/

    Authenticates user and returns JWT tokens with session tracking.
    If max sessions reached, oldest session is auto-invalidated.
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request, *args, **kwargs):
        """
        Override post to add session tracking and audit logging.

        Args:
            request: HTTP request
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Response with tokens and session info
        """
        # Get the response from parent class
        response = super().post(request, *args, **kwargs)

        if response.status_code != status.HTTP_200_OK:
            return response

        # Get user from response data (already set by LoginSerializer)
        user_id = response.data.get("user", {}).get("id")
        if not user_id:
            return response

        # Fetch user from database
        from apps.accounts.models import User

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return response

        # Create session atomically (handles limit enforcement internally)
        session, tokens = AuthService.create_session(user, request)

        # Log successful login
        AuditService.log_login(user, request)

        # Update response with session info
        response.data["session_id"] = str(session.id)
        response.data["email_verified"] = user.email_verified

        # Add warning if shopkeeper is not verified
        if (
            user.role == user.Role.SHOPKEEPER
            and hasattr(user, "shopkeeperprofile")
            and not user.shopkeeperprofile.is_verified
        ):
            response.data["warning"] = constants.SHOPKEEPER_PENDING_VERIFICATION_WARNING

        return response
