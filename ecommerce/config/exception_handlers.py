"""
Custom Exception Handlers

Provides JSON responses for all API errors instead of HTML.
Handles 404, 500, and other exceptions gracefully.
"""

from typing import Optional, Dict, Any
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404, JsonResponse
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(
    exc: Exception, context: Dict[str, Any]
) -> Optional[Response]:
    """
    Custom exception handler for DRF.

    Returns JSON responses for all exceptions instead of HTML.

    Args:
        exc: The exception that was raised
        context: Context information about the exception

    Returns:
        Response: JSON response with error details
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # DRF handled it, customize the response format
        custom_response = {
            "error": True,
            "status_code": response.status_code,
            "message": get_error_message(exc),
            "details": response.data,
        }

        # Log the error
        if response.status_code >= 500:
            logger.error(
                f"Server error: {exc}", exc_info=True, extra={"context": context}
            )

        response.data = custom_response
        return response

    # Handle exceptions not handled by DRF
    if isinstance(exc, Http404):
        return Response(
            {
                "error": True,
                "status_code": status.HTTP_404_NOT_FOUND,
                "message": "Resource not found",
                "details": {"error": "The requested resource does not exist"},
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, PermissionDenied):
        return Response(
            {
                "error": True,
                "status_code": status.HTTP_403_FORBIDDEN,
                "message": "Permission denied",
                "details": {
                    "error": "You do not have permission to access this resource"
                },
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # Log unexpected errors
    logger.error(f"Unexpected error: {exc}", exc_info=True, extra={"context": context})

    # Generic 500 error
    return Response(
        {
            "error": True,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal server error",
            "details": {
                "error": "An unexpected error occurred. Please try again later."
            },
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def get_error_message(exc: Exception) -> str:
    """
    Extract user-friendly error message from exception.

    Args:
        exc: The exception

    Returns:
        str: User-friendly error message
    """
    if hasattr(exc, "detail"):
        if isinstance(exc.detail, dict):
            # Get first error message
            for key, value in exc.detail.items():
                if isinstance(value, list):
                    return str(value[0])
                return str(value)
        return str(exc.detail)

    return str(exc)


def handler404(request, exception=None):
    """
    Custom 404 handler for all requests.

    Returns JSON response for all requests (API-only backend).
    """
    return JsonResponse(
        {
            "error": True,
            "status_code": 404,
            "message": "Not found",
            "details": {
                "path": request.path,
                "method": request.method,
                "error": f"The requested resource {request.path} does not exist",
            },
        },
        status=404,
    )


def handler500(request):
    """
    Custom 500 handler for all requests.

    Returns JSON response for all requests (API-only backend).
    """
    return JsonResponse(
        {
            "error": True,
            "status_code": 500,
            "message": "Internal server error",
            "details": {
                "error": "An unexpected error occurred. Our team has been notified."
            },
        },
        status=500,
    )


def handler403(request, exception=None):
    """
    Custom 403 handler for all requests.

    Returns JSON response for all requests (API-only backend).
    """
    return JsonResponse(
        {
            "error": True,
            "status_code": 403,
            "message": "Permission denied",
            "details": {"error": "You do not have permission to access this resource"},
        },
        status=403,
    )


def handler400(request, exception=None):
    """
    Custom 400 handler for all requests.

    Returns JSON response for all requests (API-only backend).
    """
    return JsonResponse(
        {
            "error": True,
            "status_code": 400,
            "message": "Bad request",
            "details": {
                "error": "The request could not be understood or was malformed"
            },
        },
        status=400,
    )
