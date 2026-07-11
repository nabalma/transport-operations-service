from apps.fleet.views import CarrierViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("carriers", CarrierViewSet, basename="carrier")

urlpatterns = router.urls