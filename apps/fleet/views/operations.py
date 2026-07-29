
from apps.fleet.models import Downtime,ReturnToService
from apps.fleet.serializers import DowntimeSerializer, ReturnToServiceSerializer
from .mixins import AuditUserMixin, SoftDeleteMixin
from rest_framework.viewsets import ModelViewSet






class DowntimeViewSet(AuditUserMixin,SoftDeleteMixin, ModelViewSet,):
    queryset = (Downtime.objects
        .select_related("vehicle")
        .filter(is_deleted=False)
    )
    serializer_class = DowntimeSerializer
  

class ReturnToServiceViewSet(AuditUserMixin,SoftDeleteMixin, ModelViewSet,):
    queryset = (ReturnToService.objects
        .select_related("vehicle")
        .filter(is_deleted=False)
    )
    serializer_class = ReturnToServiceSerializer
  


