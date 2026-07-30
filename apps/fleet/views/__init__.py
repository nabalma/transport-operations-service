from .availabilities import (
    NextTripEligibilityEvaluationReasonViewSet,
    NextTripEligibilityEvaluationViewSet,
    VehicleAvailabilityEvaluationReasonViewSet,
    VehicleAvailabilityEvaluationViewSet,
)
from .carriers import CarrierViewSet
from .defects import (
    DefectReleaseRequestViewSet,
    DefectReleaseValidationViewSet,
    DefectViewSet,
)
from .maintenances import (
    MaintenancePolicyViewSet,
    MaintenanceComponentViewSet,
    MaintenanceWorkOrderItemViewSet,
)
from .evidences import EvidenceViewSet
from .inspections import (
    InspectionChapterViewSet,
    InspectionCriterionResultViewSet,
    InspectionCriterionViewSet,
    InspectionScoringPolicyConfigurationViewSet,
    InspectionSectionViewSet,
    InspectionVersionViewSet,
    InspectionViewSet,
)
from .operations import (
    DowntimeViewSet,
    ReturnToServiceViewSet,
)
from .vehicles import (
    TankerCompartmentViewSet,
    VehicleAgePolicyConfigurationViewSet,
    VehicleDocumentViewSet,
    VehicleMembershipRequestViewSet,
    VehicleMembershipViewSet,
    VehicleViewSet,
)

__all__ = [
    "CarrierViewSet",
   "MaintenancePolicyViewSet",
   "MaintenanceComponentViewSet",
   "MaintenanceWorkOrderItemViewSet",
    "DefectReleaseRequestViewSet",
    "DefectReleaseValidationViewSet",
    "DefectViewSet",
    "DowntimeViewSet",
    "EvidenceViewSet",
    "InspectionChapterViewSet",
    "InspectionCriterionResultViewSet",
    "InspectionCriterionViewSet",
    "InspectionScoringPolicyConfigurationViewSet",
    "InspectionSectionViewSet",
    "InspectionVersionViewSet",
    "InspectionViewSet",
    "NextTripEligibilityEvaluationReasonViewSet",
    "NextTripEligibilityEvaluationViewSet",
    "ReturnToServiceViewSet",
    "TankerCompartmentViewSet",
    "VehicleAgePolicyConfigurationViewSet",
    "VehicleAvailabilityEvaluationReasonViewSet",
    "VehicleAvailabilityEvaluationViewSet",
    "VehicleDocumentViewSet",
    "VehicleMembershipRequestViewSet",
    "VehicleMembershipViewSet",
    "VehicleViewSet",
]