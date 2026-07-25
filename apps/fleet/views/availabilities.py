
from .mixins import AuditUserMixin, SoftDeleteMixin
from apps.fleet.selectors import list_next_trip_eligibility_evaluations, list_vehicle_availability_evaluations
from rest_framework.viewsets import ModelViewSet

from apps.fleet.models import NextTripEligibilityEvaluationReason,VehicleAvailabilityEvaluationReason
from apps.fleet.serializers import NextTripEligibilityEvaluationReasonSerializer, NextTripEligibilityEvaluationSerializer, VehicleAvailabilityEvaluationReasonSerializer, VehicleAvailabilityEvaluationSerializer 


class VehicleAvailabilityEvaluationViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = list_vehicle_availability_evaluations()
    serializer_class = VehicleAvailabilityEvaluationSerializer
  

class VehicleAvailabilityEvaluationReasonViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = (
        VehicleAvailabilityEvaluationReason.objects
        .select_related(
            "evaluation",
            "evaluation__vehicle",
        )
        .filter(is_deleted=False)
    )
    serializer_class = VehicleAvailabilityEvaluationReasonSerializer
  

class NextTripEligibilityEvaluationViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = list_next_trip_eligibility_evaluations()
    serializer_class = NextTripEligibilityEvaluationSerializer
  


class NextTripEligibilityEvaluationReasonViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = (NextTripEligibilityEvaluationReason.objects
        .select_related("evaluation")
        .filter(is_deleted=False)
    )
    serializer_class = NextTripEligibilityEvaluationReasonSerializer
  