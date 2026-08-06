
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

from .downtimes import (
DowntimePermission,
ReturnToServicePermission,
)

from .defects import (
SubmitDefectReleaseRequestPermission,
GenerateWorkOrderPermission,
ValidateDefectReleaseRequestPermission,
DefectReleaseRequestPermission,
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


    # Downtimes
    "DowntimePermission",
    "ReturnToServicePermission",


    # Memberships
    "VehicleMembershipPermission",
    "VehicleMembershipRequestPermission",


    # Defects
    "SubmitDefectReleaseRequestPermission",
    "GenerateWorkOrderPermission",
    "ValidateDefectReleaseRequestPermission",
    "DefectReleaseRequestPermission",


    # Vehicles
    "VehiclePermission",
    "VehicleAgePolicyConfigurationPermission",

]