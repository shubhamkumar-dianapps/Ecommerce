"""
Session Management Views

Handles user session listing, revocation with pagination and filtering.
"""

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from apps.accounts.serializers.session import (
    UserSessionSerializer,
    RevokeSessionSerializer,
)
from apps.accounts.services import AuthService, AuditService
from apps.accounts.pagination import SessionPagination
from apps.accounts import constants


class ActiveSessionsView(generics.ListAPIView):
    """
    List Active Sessions Endpoint

    GET /api/v1/accounts/sessions/

    Lists all active sessions for the current user with pagination.
    Supports filtering by IP address and ordering by date.
    """

    serializer_class = UserSessionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SessionPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["ip_address", "is_active"]
    ordering_fields = ["created_at", "last_activity"]
    ordering = ["-last_activity"]  # Default ordering

    def get_queryset(self):
        """
        Get queryset filtered to current user's sessions.

        Returns:
            QuerySet of user's sessions
        """
        return AuthService.get_active_sessions(self.request.user)


class RevokeSessionView(APIView):
    """
    Revoke Session Endpoint

    POST /api/v1/accounts/sessions/revoke/

    Revokes a specific session by ID.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = RevokeSessionSerializer

    def post(self, request) -> Response:
        """
        Revoke a session.

        Args:
            request: HTTP request with session_id in body

        Returns:
            Success or error response
        """
        serializer = RevokeSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data["session_id"]

        # Invalidate session
        success, message = AuthService.invalidate_session(session_id)

        if success:
            # Log session revocation
            AuditService.log_session_revoked(request.user, request, session_id)
            return Response(
                {"message": message or constants.SESSION_REVOKED_SUCCESS},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": message or constants.SESSION_NOT_FOUND},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RevokeAllSessionsView(APIView):
    """
    Revoke All Sessions Endpoint

    POST /api/v1/accounts/sessions/revoke-all/

    Revokes all active sessions for the current user.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        """
        Revoke all sessions.

        Args:
            request: HTTP request

        Returns:
            Success response with count of revoked sessions
        """
        # Revoke all sessions
        count = AuthService.invalidate_all_sessions(request.user)

        # Log event
        AuditService.log_session_revoked(
            request.user, request, metadata={"revoked_count": count}
        )

        return Response(
            {"message": constants.SESSIONS_REVOKED_COUNT.format(count=count)},
            status=status.HTTP_200_OK,
        )
