from django.contrib import admin
from django.urls import path, include
from django.conf import settings
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


urlpatterns = [
    path("admin/", admin.site.urls),
    # Health check endpoint (no auth required)
    path("api/health/", health_check, name="health_check"),
    # API v1 routes - all endpoints under /api/v1/ for consistent versioning
    path("api/v1/accounts/", include("apps.accounts.urls")),
    path("api/v1/addresses/", include("apps.addresses.urls")),
    path("api/v1/products/", include("apps.products.urls")),
    path("api/v1/cart/", include("apps.cart.urls")),
    path("api/v1/orders/", include("apps.orders.urls")),
    path("api/v1/reviews/", include("apps.reviews.urls")),
]

# Add Silk profiling URLs in DEBUG mode
if settings.DEBUG:
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]

# Custom error handlers for graceful JSON responses
handler400 = "config.exception_handlers.handler400"
handler403 = "config.exception_handlers.handler403"
handler404 = "config.exception_handlers.handler404"
handler500 = "config.exception_handlers.handler500"
