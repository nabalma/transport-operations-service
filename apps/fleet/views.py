from apps.fleet.mixins import AuditUserMixin, SoftDeleteMixin
from apps.fleet.permissions import InspectionConfigurationPermission, InspectionPermission, VehiclePermission
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from apps.fleet.models import Carrier, CorrectiveAction, Defect, DefectReleaseValidation, Downtime, Evidence, FleetMembership, Inspection, InspectionContextCriterion, InspectionContextSection, InspectionCriterion, InspectionCriterionResult, InspectionSection, Maintenance, NextTripEligibilityEvaluation, NextTripEligibilityEvaluationReason, ReturnToService, TankerCompartment, Vehicle, VehicleAvailabilityEvaluation, VehicleAvailabilityEvaluationReason, VehicleDocument
from apps.fleet.serializers import CarrierSerializer, CorrectiveActionSerializer, DefectReleaseValidationSerializer, DefectSerializer, DowntimeSerializer, EvidenceSerializer, FleetMembershipSerializer, InspectionContextCriterionSerializer, InspectionContextSectionSerializer, InspectionCriterionResultSerializer, InspectionCriterionSerializer, InspectionSectionSerializer, InspectionSerializer, MaintenanceSerializer, NextTripEligibilityEvaluationReasonSerializer, NextTripEligibilityEvaluationSerializer, ReturnToServiceSerializer, TankerCompartmentSerializer, VehicleAvailabilityEvaluationReasonSerializer, VehicleAvailabilityEvaluationSerializer, VehicleDocumentSerializer, VehicleSerializer


class CarrierViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet):
    queryset = Carrier.objects.prefetch_related("vehicles")
    serializer_class = CarrierSerializer


   

class VehicleViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet):
   queryset = Vehicle.objects.select_related("carrier").prefetch_related( "tanker_compartments","fleet_memberships","documents").filter(is_deleted=False)
   serializer_class = VehicleSerializer
   permission_classes=[VehiclePermission]


class TankerCompartmentViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = TankerCompartment.objects.filter(is_deleted=False)
    serializer_class = TankerCompartmentSerializer
  

class FleetMembershipViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = FleetMembership.objects.filter(is_deleted=False)
    serializer_class = FleetMembershipSerializer
  


class VehicleDocumentViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = VehicleDocument.objects.filter(is_deleted=False)
    serializer_class = VehicleDocumentSerializer
  


class InspectionSectionViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = InspectionSection.objects.filter(is_deleted=False)
    serializer_class = InspectionSectionSerializer
    permission_classes = [InspectionConfigurationPermission]

class InspectionCriterionViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = InspectionCriterion.objects.filter(is_deleted=False)
    serializer_class = InspectionCriterionSerializer
    permission_classes = [InspectionConfigurationPermission]


class InspectionContextSectionViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = (
        InspectionContextSection.objects
        .select_related("section")
        .filter(is_deleted=False)
    )
    serializer_class = InspectionContextSectionSerializer
    permission_classes = [InspectionConfigurationPermission]


class InspectionContextCriterionViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = (InspectionContextCriterion.objects
        .select_related("context_section","criterion").filter(is_deleted=False))
    serializer_class = InspectionContextCriterionSerializer
    permission_classes = [InspectionConfigurationPermission]

class InspectionViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = (Inspection.objects
    .select_related("vehicle")
    .prefetch_related("criterion_results","criterion_results__context_criterion","criterion_results__context_criterion__criterion",)
    .filter(is_deleted=False)
)
    serializer_class = InspectionSerializer
    permission_classes = [InspectionPermission]

class InspectionCriterionResultViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = (
        InspectionCriterionResult.objects.select_related("inspection","context_criterion","context_criterion__criterion",).filter(is_deleted=False)
    )
    serializer_class = InspectionCriterionResultSerializer
    permission_classes = [InspectionPermission]


class DefectViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = (
    Defect.objects
    .select_related("vehicle","source_inspection","source_inspection_criterion_result",)
    .prefetch_related("corrective_actions","release_validations",)
    .filter(is_deleted=False)
)
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
  

class MaintenanceViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = ( Maintenance.objects
        .select_related("vehicle")
        .filter(is_deleted=False)
    )
    serializer_class = MaintenanceSerializer
  


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
  


class VehicleAvailabilityEvaluationViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = (VehicleAvailabilityEvaluation.objects
        .select_related("vehicle")
        .filter(is_deleted=False)
    )
    serializer_class = VehicleAvailabilityEvaluationSerializer
  

class VehicleAvailabilityEvaluationReasonViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = (VehicleAvailabilityEvaluation.objects
    .select_related("vehicle")
    .prefetch_related("evaluation_reasons")
    .filter(is_deleted=False)
    )
    serializer_class = VehicleAvailabilityEvaluationReasonSerializer
  


class NextTripEligibilityEvaluationViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = (NextTripEligibilityEvaluation.objects
    .select_related("vehicle")
    .prefetch_related("evaluation_reasons")
    .filter(is_deleted=False)
)
    serializer_class = NextTripEligibilityEvaluationSerializer
  


class NextTripEligibilityEvaluationReasonViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = (NextTripEligibilityEvaluationReason.objects
        .select_related("evaluation")
        .filter(is_deleted=False)
    )
    serializer_class = NextTripEligibilityEvaluationReasonSerializer
  

class EvidenceViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = Evidence.objects.filter(is_deleted=False)
    serializer_class = EvidenceSerializer
