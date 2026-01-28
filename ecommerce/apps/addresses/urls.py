"""
Address URLs

URL routing for address endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.addresses.views import AddressViewSet

# Create router for viewset
router = DefaultRouter()
router.register(r"", AddressViewSet, basename="address")

app_name = "addresses"

urlpatterns = [
    path("", include(router.urls)),
]
