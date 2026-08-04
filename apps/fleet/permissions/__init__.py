
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
)

from .memberships import (
VehicleMembershipPermission,
VehicleMembershipRequestPermission,
)

from .vehicles import (
VehiclePermission,
VehicleAgePolicyConfigurationPermission,
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


    # Memberships
    "VehicleMembershipPermission",
    "VehicleMembershipRequestPermission",



    # Vehicles
    "VehiclePermission",
    "VehicleAgePolicyConfigurationPermission",

]