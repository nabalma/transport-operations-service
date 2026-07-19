from apps.fleet.mixins import AuditUserMixin, SoftDeleteMixin
from apps.fleet.permissions import InspectionConfigurationPermission, InspectionPermission, VehicleAgePolicyConfigurationPermission, VehicleMembershipPermission, VehicleMembershipRequestPermission, VehiclePermission
from apps.fleet.services.inspections import build_blank_inspection_sheet, create_inspection_version, update_inspection_version_status
from apps.fleet.services.membership_requests import approve_vehicle_membership_request, cancel_vehicle_membership_request, create_vehicle_membership_request, reject_vehicle_membership_request, submit_vehicle_membership_request
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response


from apps.fleet.models import Carrier, CorrectiveAction, Defect, DefectReleaseValidation, Downtime, Evidence, Inspection, InspectionCriterion, InspectionCriterionResult, InspectionSection, InspectionContextVersion, Maintenance, NextTripEligibilityEvaluation, NextTripEligibilityEvaluationReason, ReturnToService, TankerCompartment, Vehicle, VehicleAgePolicyConfiguration, VehicleAvailabilityEvaluation, VehicleAvailabilityEvaluationReason, VehicleDocument, VehicleMembership, VehicleMembershipRequest
from apps.fleet.serializers import CarrierSerializer, CorrectiveActionSerializer, DefectReleaseValidationSerializer, DefectSerializer, DowntimeSerializer, EvidenceSerializer, InspectionContextVersionSerializer, InspectionCriterionResultSerializer, InspectionCriterionSerializer, InspectionSectionSerializer, InspectionSerializer, InspectionContextVersionSerializer, MaintenanceSerializer, NextTripEligibilityEvaluationReasonSerializer, NextTripEligibilityEvaluationSerializer, ReturnToServiceSerializer, TankerCompartmentSerializer, VehicleAgePolicyConfigurationSerializer, VehicleAvailabilityEvaluationReasonSerializer, VehicleAvailabilityEvaluationSerializer, VehicleDocumentSerializer, VehicleMembershipRequestSerializer, VehicleMembershipSerializer, VehicleSerializer


class CarrierViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet):
    queryset = Carrier.objects.prefetch_related("vehicles")
    serializer_class = CarrierSerializer


class VehicleAgePolicyConfigurationViewSet(AuditUserMixin,ModelViewSet,):
    queryset = VehicleAgePolicyConfiguration.objects.all()
    serializer_class = VehicleAgePolicyConfigurationSerializer
    permission_classes = [VehicleAgePolicyConfigurationPermission]

    
       

class VehicleViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet):
   queryset = Vehicle.objects.select_related("carrier").prefetch_related( "tanker_compartments","vehicle_memberships","documents").filter(is_deleted=False)
   serializer_class = VehicleSerializer
   permission_classes=[VehiclePermission]


class TankerCompartmentViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = TankerCompartment.objects.filter(is_deleted=False)
    serializer_class = TankerCompartmentSerializer
    permission_classes=[VehiclePermission]
  

class VehicleMembershipViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = VehicleMembership.objects.filter(is_deleted=False)
    serializer_class = VehicleMembershipSerializer
    permission_classes =[VehicleMembershipPermission]
  

class VehicleMembershipRequestViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = VehicleMembershipRequest.objects.filter(is_deleted=False)
    serializer_class = VehicleMembershipRequestSerializer
    permission_classes =[VehicleMembershipRequestPermission]


    # action pour la creation de la request
    def perform_create(self, serializer):
        membership_request = create_vehicle_membership_request(
            vehicle_id=serializer.validated_data["vehicle"].id,
            requested_entry_date=serializer.validated_data["requested_entry_date"],
            membership_type=serializer.validated_data["membership_type"],
            created_by=self.request.user,
        )

        serializer.instance = membership_request

    # Pour la soumission de la requete. Lurl devra etre
    # POST /api/fleet/vehicle-membership-requests/<id>/submit/
    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        membership_request = self.get_object()

        submitted_request = submit_vehicle_membership_request(
        membership_request_id=membership_request.id,
        submitted_by=request.user,
        )
        serializer = self.get_serializer(submitted_request)
        return Response(serializer.data,status=status.HTTP_200_OK,)
    
  # Pour lannulation de la requete. Lurl devra etre
    # POST /api/fleet/vehicle-membership-requests/<id>/cancel/
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        membership_request = self.get_object()

        cancelled_request = cancel_vehicle_membership_request(
            membership_request_id=membership_request.id,
            cancelled_by=request.user,
        )

        serializer = self.get_serializer(cancelled_request)
        return Response(serializer.data,status=status.HTTP_200_OK,)
    

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        membership_request = self.get_object()

        approved_request = approve_vehicle_membership_request(
        membership_request_id=membership_request.id,
        approved_by=request.user,
        decision_comment=request.data.get("decision_comment"),
        )

        serializer = self.get_serializer(approved_request)

        return Response(serializer.data,status=status.HTTP_200_OK,)


    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        membership_request = self.get_object()

        rejected_request = reject_vehicle_membership_request(
        membership_request_id=membership_request.id,
        rejected_by=request.user,
        decision_comment=request.data.get("decision_comment"),
        )

        serializer = self.get_serializer(rejected_request)
        return Response(serializer.data,status=status.HTTP_200_OK,)
 

class VehicleDocumentViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = VehicleDocument.objects.filter(is_deleted=False)
    serializer_class = VehicleDocumentSerializer
    permission_classes=[VehiclePermission]


class InspectionContextVersionViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = InspectionContextVersion.objects.filter(is_deleted=False)
    serializer_class = InspectionContextVersionSerializer
    permission_classes = [InspectionConfigurationPermission]

    def perform_create(self, serializer):
        serializer.instance = create_inspection_version(
            context=serializer.validated_data["context"],
            version=serializer.validated_data["version"],
            source_version=serializer.validated_data.get("source_version"),
            is_current=serializer.validated_data.get("is_current", False),
            created_by=self.request.user,
        )
    def perform_update(self, serializer):
        serializer.instance = update_inspection_version_status(
            inspection_version=serializer.instance,
            is_current=serializer.validated_data["is_current"],
            updated_by=self.request.user,
    )
        

# InspectionSectionViewSet
# Gère les sections directement rattachées à une version.

class InspectionSectionViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = InspectionSection.objects.select_related("inspection_version").filter(is_deleted=False)
    serializer_class = InspectionSectionSerializer
    permission_classes = [InspectionConfigurationPermission]



# InspectionCriterionViewSet
# Gère les critères directement rattachés à une section versionnée.
class InspectionCriterionViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = InspectionCriterion.objects.select_related("section","section__inspection_version",).filter(is_deleted=False)
    serializer_class = InspectionCriterionSerializer
    permission_classes = [InspectionConfigurationPermission]


# =============================================================================
# InspectionViewSet
#
# Charge la version utilisée et les résultats avec leurs critères.
# =============================================================================
class InspectionViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = (Inspection.objects.select_related(
            "vehicle",
            "inspection_version",
        )
        .prefetch_related(
            "criterion_results",
            "criterion_results__criterion",
            "criterion_results__criterion__section",
            (
                "criterion_results__criterion__section"
                "__inspection_version"
            ),
        )
        .filter(is_deleted=False)
    )

    serializer_class = InspectionSerializer
    permission_classes = [InspectionPermission]

    # blank_sheet
    # Retourne une fiche vierge pour le contexte d’inspection demandé.
    # La version courante est automatiquement sélectionnée par le service.
    @action(detail=False,methods=["get"],url_path="blank-sheet",)
    def blank_sheet(self, request):
        """
        Construit et retourne une fiche d’inspection vierge.
        Le contexte est lu depuis les paramètres de l’URL.
        """
        inspection_context=request.query_params.get("context")
        sheet = build_blank_inspection_sheet(inspection_context=inspection_context,)

        return Response(sheet,status=status.HTTP_200_OK,)



# InspectionCriterionResultViewSet
# Charge directement le critère, sa section et sa version.
class InspectionCriterionResultViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = InspectionCriterionResult.objects.select_related(
            "inspection",
            "inspection__inspection_version",
            "criterion",
            "criterion__section",
            "criterion__section__inspection_version",
        ).filter(is_deleted=False)
    serializer_class = InspectionCriterionResultSerializer
    permission_classes = [InspectionPermission]


class DefectViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = Defect.objects .select_related("vehicle","source_inspection","source_inspection_criterion_result",
    ).prefetch_related("corrective_actions","release_validations",
    ).filter(is_deleted=False)
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




