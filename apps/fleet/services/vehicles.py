from apps.fleet.constants import CarrierStatus, VehicleStatus
from apps.fleet.models import Vehicle, VehicleAgePolicyConfiguration
from rest_framework.exceptions import ValidationError
from django.utils import timezone

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


# -------------------------------------------------------------------
# Active un véhicule après son entrée officielle dans la flotte.
# Enregistre également l'utilisateur ayant effectué la modification.
# -------------------------------------------------------------------
def activate_vehicle(*, vehicle, updated_by):
    vehicle.status = VehicleStatus.ACTIVE
    vehicle.updated_by = updated_by

    vehicle.save(update_fields=[
            "status",
            "updated_by",
            "updated_at",])

    return vehicle



# -------------------------------------------------------------------
# Récupère la politique d'âge actuellement applicable à une cible.
# Une erreur est levée si aucune politique en vigueur n'existe.
# -------------------------------------------------------------------
def _get_current_vehicle_age_policy_or_error(*, target):
    policy = VehicleAgePolicyConfiguration.objects.filter(
        target=target,
        effective_to__isnull=True,
    ).first()

    if policy is None:
        raise ValidationError(
            {
                "vehicle_age_policy": (
                    f"Aucune politique d'âge n'est définie "
                    f"pour {target}."
                )
            }
        )

    return policy

# -------------------------------------------------------------------
# Calcule l'âge du tracteur en années civiles.
# -------------------------------------------------------------------
def _calculate_tractor_age(*, vehicle):
    current_year = timezone.localdate().year
    return current_year - vehicle.tractor_manufacture_year


# -------------------------------------------------------------------
# Calcule l'âge de la citerne en années civiles.
# -------------------------------------------------------------------
def _calculate_tanker_age(*, vehicle):
    current_year = timezone.localdate().year
    return current_year - vehicle.tanker_manufacture_year


# -------------------------------------------------------------------
# Vérifie que l'âge du tracteur et de la citerne respecte
# les limites définies dans les politiques d'âge applicables.
# -------------------------------------------------------------------
def _ensure_vehicle_age_is_allowed(*,vehicle,tractor_policy,tanker_policy,):
    tractor_age = _calculate_tractor_age(vehicle=vehicle,)
    tanker_age = _calculate_tanker_age(vehicle=vehicle,)

    if tractor_age > tractor_policy.maximum_allowed_age:
        raise ValidationError(
            {
                "tractor_manufacture_year": (
                    "L'âge du tracteur dépasse la limite autorisée."
                )
            }
        )

    if tanker_age > tanker_policy.maximum_allowed_age:
        raise ValidationError(
            {
                "tanker_manufacture_year": (
                    "L'âge de la citerne dépasse la limite autorisée."
                )
            }
        )