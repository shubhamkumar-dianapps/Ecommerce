from rest_framework.routers import DefaultRouter
from apps.products.views.product import CategoryViewSet, BrandViewSet, ProductViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"brands", BrandViewSet, basename="brand")
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = router.urls
