from apps.fleet.constants import CarrierStatus
from apps.fleet.models import Vehicle
from rest_framework.exceptions import ValidationError

# -----------------------------------------------
# Récupère un véhicule existant et non supprimé.
# -----------------------------------------------

def _get_vehicle_or_error(*, vehicle_id):
    vehicle = Vehicle.objects.filter(
        id=vehicle_id,
        is_deleted=False,
    ).first()

    if vehicle is None:
        raise ValidationError(
            {"vehicle": "Ce véhicule n'existe pas."}
        )

    return vehicle



# -------------------------------------------------------------------
# Vérifie que le transporteur associé au véhicule est utilisable.
# -------------------------------------------------------------------
def _get_valid_carrier_or_error(*, vehicle):
    carrier = vehicle.carrier

    if carrier.is_deleted or carrier.status != CarrierStatus.ACTIVE:
        raise ValidationError(
            {
                "vehicle": (
                    "Le transporteur associé à ce véhicule "
                    "est supprimé ou inactif."
                )
            }
        )

    return carrier


