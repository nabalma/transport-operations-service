
from .base import (
BaseGroupPermission,
)

from .carriers import (
CarrierPermission,
)

from .inspections import (
InspectionPermission,
InspectionConfigurationPermission
)

from .maintenances import (
MaintenancePolicyPermission,
MaintenanceWorkOrderPermission,
)

from .memberships import (
VehicleMembershipPermission,
VehicleMembershipRequestPermission,
)

from .vehicles import (
VehiclePermission,
VehicleAgePolicyConfigurationPermission,
)

from .operations import (
DowntimePermission,
ReturnToServicePermission,
)

from .defects import (
SubmitDefectReleaseRequestPermission,
GenerateWorkOrderPermission,
ValidateDefectReleaseRequestPermission,
DefectReleaseRequestPermission,
)

from .availabilities import (
VehicleAvailabilityEvaluationPermission,
VehicleAvailabilityEvaluationReasonPermission,
)


__all__ = [
    # Base
    "BaseGroupPermission",

    # Carriers
    "CarrierPermission",

    # Inspections
    "InspectionPermission",
    "InspectionConfigurationPermission",


    # Maintenances
    "MaintenancePolicyPermission",
    "MaintenanceWorkOrderPermission",


    # Operations
    "DowntimePermission",
    "ReturnToServicePermission",


    # Memberships
    "VehicleMembershipPermission",
    "VehicleMembershipRequestPermission",


    # VehicleAvailabilityEvaluations
    "VehicleAvailabilityEvaluationPermission",
    "VehicleAvailabilityEvaluationReasonPermission",


    # Defects
    "SubmitDefectReleaseRequestPermission",
    "GenerateWorkOrderPermission",
    "ValidateDefectReleaseRequestPermission",
    "DefectReleaseRequestPermission",


    # Vehicles
    "VehiclePermission",
    "VehicleAgePolicyConfigurationPermission",

]