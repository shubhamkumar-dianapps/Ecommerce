from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.reviews.views import ReviewViewSet

router = DefaultRouter()
router.register(r"", ReviewViewSet, basename="review")

urlpatterns = router.urls
