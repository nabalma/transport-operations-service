from apps.fleet.models import Carrier
from apps.fleet.permissions import CarrierPermission
from apps.fleet.serializers import CarrierSerializer
from .mixins import AuditUserMixin, SoftDeleteMixin
from rest_framework.viewsets import ModelViewSet




class CarrierViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet):
    queryset = Carrier.objects.prefetch_related("vehicles")
    serializer_class = CarrierSerializer
    permission_classes = [CarrierPermission]