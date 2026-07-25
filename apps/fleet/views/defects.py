
from .mixins import AuditUserMixin, SoftDeleteMixin


from apps.fleet.selectors import list_defects_with_source_and_resolution
from rest_framework.viewsets import ModelViewSet




from apps.fleet.models import CorrectiveAction, DefectReleaseValidation
from apps.fleet.serializers import CorrectiveActionSerializer, DefectReleaseValidationSerializer, DefectSerializer



class DefectViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = list_defects_with_source_and_resolution()
    serializer_class = DefectSerializer


class CorrectiveActionViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = (CorrectiveAction.objects
        .select_related("defect")
        .filter(is_deleted=False)
    )
    serializer_class = CorrectiveActionSerializer
 


class DefectReleaseValidationViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = (DefectReleaseValidation.objects
        .select_related("defect")
        .filter(is_deleted=False))
    serializer_class = DefectReleaseValidationSerializer
  