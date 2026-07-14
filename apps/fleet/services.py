from apps.fleet.constants import CarrierStatus, VehicleMembershipRequestStatus, VehicleMembershipStatus
from apps.fleet.models import Vehicle, VehicleMembership, VehicleMembershipRequest
from rest_framework.exceptions import ValidationError
# -------------------------------------------------------------------
# Récupère un véhicule existant et non supprimé.
# -------------------------------------------------------------------
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
# Vérifie que le véhicule n'appartient pas déjà à la flotte.
# -------------------------------------------------------------------
def _ensure_vehicle_has_no_active_membership(*, vehicle):
    has_active_membership = VehicleMembership.objects.filter(
        vehicle=vehicle,
        status=VehicleMembershipStatus.ACTIVE,
        exit_date__isnull=True,
        is_deleted=False,
    ).exists()

    if has_active_membership:
        raise ValidationError(
            {"vehicle": "Ce véhicule appartient déjà à la flotte."}
        )


# -------------------------------------------------------------------
# Vérifie qu'aucune demande ouverte n'existe déjà pour le véhicule.
# -------------------------------------------------------------------
def _ensure_vehicle_has_no_open_request(*, vehicle):
    has_open_request = VehicleMembershipRequest.objects.filter(
        vehicle=vehicle,
        status__in=[
            VehicleMembershipRequestStatus.DRAFT,
            VehicleMembershipRequestStatus.PENDING,
        ],
        is_deleted=False,
    ).exists()

    if has_open_request:
        raise ValidationError(
            {
                "vehicle": (
                    "Une demande d'appartenance est déjà "
                    "en cours pour ce véhicule."
                )
            }
        )


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
# Crée une demande d'appartenance d'un véhicule à la flotte.
#
# Étapes :
# 1. Récupérer le véhicule.
# 2. Vérifier qu'il n'est pas déjà dans la flotte.
# 3. Vérifier qu'il n'a pas déjà une demande ouverte.
# 4. Vérifier que son transporteur est valide.
# 5. Créer et retourner la demande.
# -------------------------------------------------------------------
def create_vehicle_membership_request(*,vehicle_id,requested_entry_date,membership_type,created_by,):
    
    vehicle = _get_vehicle_or_error(vehicle_id=vehicle_id)
    _ensure_vehicle_has_no_active_membership(vehicle=vehicle)
    _ensure_vehicle_has_no_open_request(vehicle=vehicle)
    _get_valid_carrier_or_error(vehicle=vehicle)

    return VehicleMembershipRequest.objects.create(
        vehicle=vehicle,
        requested_entry_date=requested_entry_date,
        membership_type=membership_type,
        created_by=created_by,
        updated_by=created_by,
    )