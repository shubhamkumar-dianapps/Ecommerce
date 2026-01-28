from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/v1/accounts/", include("apps.accounts.urls")
    ),  # Now includes /api/v1/accounts/
    path("api/v1/addresses/", include("apps.addresses.urls")),
    path("api/", include("apps.products.urls")),
    path("api/cart/", include("apps.cart.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/reviews/", include("apps.reviews.urls")),
]

# Custom error handlers for graceful JSON responses
handler400 = "config.exception_handlers.handler400"
handler403 = "config.exception_handlers.handler403"
handler404 = "config.exception_handlers.handler404"
handler500 = "config.exception_handlers.handler500"
