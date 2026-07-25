from .availabilities import (
    NextTripEligibilityEvaluationReasonViewSet,
    NextTripEligibilityEvaluationViewSet,
    VehicleAvailabilityEvaluationReasonViewSet,
    VehicleAvailabilityEvaluationViewSet,
)
from .carriers import CarrierViewSet
from .defects import (
    CorrectiveActionViewSet,
    DefectReleaseValidationViewSet,
    DefectViewSet,
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
    MaintenanceViewSet,
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
    "CorrectiveActionViewSet",
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
    "MaintenanceViewSet",
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