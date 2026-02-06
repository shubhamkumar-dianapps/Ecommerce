from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from .views import health_check


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

# Add Silk profiling URLs in DEBUG mode (optional dependency)
if settings.DEBUG:
    try:
        import silk  # noqa: F401

        urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
    except ImportError:
        pass  # Silk not installed, skip profiling URLs

# Custom error handlers for graceful JSON responses
handler400 = "config.exception_handlers.handler400"
handler403 = "config.exception_handlers.handler403"
handler404 = "config.exception_handlers.handler404"
handler500 = "config.exception_handlers.handler500"
