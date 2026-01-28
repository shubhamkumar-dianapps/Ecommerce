from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.orders.views.order import OrderViewSet

router = DefaultRouter()
router.register(r"", OrderViewSet, basename="order")

urlpatterns = router.urls
