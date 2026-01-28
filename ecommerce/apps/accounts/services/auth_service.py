from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import UserSession


class AuthService:
    @staticmethod
    def get_tokens_for_user(user):
        """Generate JWT tokens for user"""
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    @staticmethod
    def create_session(user, request):
        """
        Create a new session for the user.
        Returns the UserSession object.
        """
        # Generate a unique session key (using JWT token as session key)
        tokens = AuthService.get_tokens_for_user(user)
        session_key = tokens["refresh"]  # Use refresh token as session identifier

        # Extract IP and user agent
        ip_address = AuthService._get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        # Create session
        session = UserSession.objects.create(
            user=user,
            session_key=session_key,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return session, tokens

    @staticmethod
    def invalidate_session(session_id):
        """Invalidate a specific session"""
        try:
            session = UserSession.objects.get(id=session_id, is_active=True)
            session.invalidate()
            return True, "Session invalidated successfully"
        except UserSession.DoesNotExist:
            return False, "Session not found or already inactive"

    @staticmethod
    def get_active_sessions(user):
        """Get all active sessions for a user"""
        return UserSession.objects.filter(user=user, is_active=True)

    @staticmethod
    def invalidate_all_sessions(user, except_session_id=None):
        """Invalidate all sessions for a user except optionally one"""
        sessions = UserSession.objects.filter(user=user, is_active=True)
        if except_session_id:
            sessions = sessions.exclude(id=except_session_id)

        count = sessions.update(is_active=False)
        return count

    @staticmethod
    def _get_client_ip(request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    @staticmethod
    def count_active_sessions(user) -> int:
        """Count active sessions for a user"""
        return UserSession.objects.filter(user=user, is_active=True).count()

    @staticmethod
    def has_max_active_sessions(user) -> bool:
        """Check if user has reached maximum active sessions limit"""
        from apps.accounts import constants

        return (
            AuthService.count_active_sessions(user)
            >= constants.MAX_ACTIVE_SESSIONS_PER_USER
        )
