"""
Core API Views

Health check and other core endpoints that don't belong to specific apps.
"""

from django.http import JsonResponse
from django.db import connection


def health_check(request):
    """
    Health check endpoint for load balancers and monitoring.

    GET /api/health/

    Returns:
        - 200 OK with {"status": "healthy", "database": "connected"}
        - 503 Service Unavailable if database is down
    """
    try:
        # Check database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "connected"
        status_code = 200
    except Exception:
        db_status = "disconnected"
        status_code = 503

    return JsonResponse(
        {
            "status": "healthy" if status_code == 200 else "unhealthy",
            "database": db_status,
        },
        status=status_code,
    )
