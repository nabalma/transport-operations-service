
from apps.fleet.models import Evidence
from apps.fleet.serializers import EvidenceSerializer

from .mixins import AuditUserMixin, SoftDeleteMixin
from rest_framework.viewsets import ModelViewSet


class EvidenceViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = Evidence.objects.filter(is_deleted=False)
    serializer_class = EvidenceSerializer


