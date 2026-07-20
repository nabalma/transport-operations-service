from apps.fleet.views import CarrierViewSet, CorrectiveActionViewSet, DefectReleaseValidationViewSet, DefectViewSet, DowntimeViewSet, EvidenceViewSet, InspectionVersionViewSet, InspectionCriterionResultViewSet, InspectionCriterionViewSet, InspectionSectionViewSet, InspectionViewSet, MaintenanceViewSet, NextTripEligibilityEvaluationReasonViewSet, NextTripEligibilityEvaluationViewSet, ReturnToServiceViewSet, TankerCompartmentViewSet, VehicleAgePolicyConfigurationViewSet, VehicleAvailabilityEvaluationReasonViewSet, VehicleAvailabilityEvaluationViewSet, VehicleDocumentViewSet, VehicleMembershipRequestViewSet, VehicleMembershipViewSet, VehicleViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("carriers", CarrierViewSet, basename="carrier")
router.register("vehicle-age-policy-configurations",VehicleAgePolicyConfigurationViewSet,basename="vehicle-age-policy-configuration",)
router.register("vehicles", VehicleViewSet, basename="vehicle")
router.register("tanker-compartments",TankerCompartmentViewSet, basename = "tanker-compartment")
router.register("vehicle-memberships",VehicleMembershipViewSet,basename="vehicle-membership",)
router.register("vehicle-membership-requests",VehicleMembershipRequestViewSet,basename="vehicle-membership-request",)
router.register("vehicle-documents",VehicleDocumentViewSet,basename="vehicle-document",)
router.register("inspection-versions",InspectionVersionViewSet,basename="inspection-version",)
router.register("inspection-sections",InspectionSectionViewSet,basename="inspection-section",)
router.register("inspection-criteria",InspectionCriterionViewSet,basename="inspection-criterion",)
router.register("inspections",InspectionViewSet,basename="inspection",)
router.register("inspection-criterion-results",InspectionCriterionResultViewSet,basename="inspection-criterion-result",)
router.register("defects",DefectViewSet,basename="defect",)
router.register("corrective-actions",CorrectiveActionViewSet,basename="corrective-action",)
router.register("defect-release-validations",DefectReleaseValidationViewSet,basename="defect-release-validation",)
router.register("maintenances", MaintenanceViewSet,basename="maintenance",)
router.register("downtimes",DowntimeViewSet,basename="downtime",)
router.register("return-to-services",ReturnToServiceViewSet,basename="return-to-service",)
router.register("vehicle-availability-evaluations",VehicleAvailabilityEvaluationViewSet,basename="vehicle-availability-evaluation",)
router.register("vehicle-availability-evaluation-reasons",VehicleAvailabilityEvaluationReasonViewSet,basename="vehicle-availability-evaluation-reason",)
router.register("next-trip-eligibility-evaluations",NextTripEligibilityEvaluationViewSet,basename="next-trip-eligibility-evaluation",)
router.register("next-trip-eligibility-evaluation-reasons",NextTripEligibilityEvaluationReasonViewSet,basename="next-trip-eligibility-evaluation-reason",)
router.register("evidences",EvidenceViewSet,basename="evidence",)

urlpatterns = router.urls