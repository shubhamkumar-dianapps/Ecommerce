"""
Utility Functions for Accounts App

Reusable helper functions to avoid code duplication.
"""

from typing import Optional
from django.http import HttpRequest
from django.conf import settings


def get_client_ip(request: HttpRequest) -> Optional[str]:
    """
    Extract client IP address from request.

    SECURITY: Only uses X-Forwarded-For when USE_X_FORWARDED_HOST is True
    (indicating the app is behind a trusted proxy). Otherwise uses REMOTE_ADDR
    to prevent IP spoofing attacks.

    Args:
        request: HTTP request object

    Returns:
        Client IP address string or None if not available
    """
    # Only trust X-Forwarded-For if behind a trusted proxy
    if getattr(settings, "USE_X_FORWARDED_HOST", False):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # Take the first IP (client IP) from the chain
            return x_forwarded_for.split(",")[0].strip()

    # Default: use REMOTE_ADDR (direct connection IP)
    return request.META.get("REMOTE_ADDR")


def get_user_agent(request: HttpRequest) -> str:
    """
    Extract user agent from request.

    Args:
        request: HTTP request object

    Returns:
        User agent string (empty string if not available)
    """
    return request.META.get("HTTP_USER_AGENT", "")
