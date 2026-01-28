"""
Utility Functions for Accounts App

Reusable helper functions to avoid code duplication.
"""

from typing import Optional
from django.http import HttpRequest


def get_client_ip(request: HttpRequest) -> Optional[str]:
    """
    Extract client IP address from request.

    Handles X-Forwarded-For header for proxied requests.

    Args:
        request: HTTP request object

    Returns:
        Client IP address string or None if not available
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_user_agent(request: HttpRequest) -> str:
    """
    Extract user agent from request.

    Args:
        request: HTTP request object

    Returns:
        User agent string (empty string if not available)
    """
    return request.META.get("HTTP_USER_AGENT", "")
