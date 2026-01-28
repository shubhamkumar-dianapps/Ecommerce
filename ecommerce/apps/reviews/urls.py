"""
Reviews App URLs

URL configuration for review endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.reviews.views import ReviewViewSet

app_name = "reviews"

# Create router
router = DefaultRouter()

# Register viewsets
router.register(r"", ReviewViewSet, basename="review")

urlpatterns = [
    path("", include(router.urls)),
]
