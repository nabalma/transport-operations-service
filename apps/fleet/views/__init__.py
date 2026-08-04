from .availabilities import (
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
    MaintenanceWorkOrderViewSet,
    MaintenanceScheduleViewSet,
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
    DowntimeCauseViewSet,
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
   "MaintenanceWorkOrderViewSet",
   "MaintenanceScheduleViewSet",
    "DefectReleaseRequestViewSet",
    "DefectReleaseValidationViewSet",
    "DefectViewSet",
    "DowntimeViewSet",
    "DowntimeCauseViewSet",
    "EvidenceViewSet",
    "InspectionChapterViewSet",
    "InspectionCriterionResultViewSet",
    "InspectionCriterionViewSet",
    "InspectionScoringPolicyConfigurationViewSet",
    "InspectionSectionViewSet",
    "InspectionVersionViewSet",
    "InspectionViewSet",
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