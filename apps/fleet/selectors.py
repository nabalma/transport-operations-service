from apps.fleet.constants import VehicleMembershipStatus
from apps.fleet.models import Defect, Inspection, InspectionCriterion, NextTripEligibilityEvaluation, Vehicle, VehicleAvailabilityEvaluation, VehicleMembershipRequest
from rest_framework.exceptions import ValidationError
from django.db.models import QuerySet

#====================
#     VEHICULES
#====================

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


def list_vehicles() -> QuerySet[Vehicle]:
    return (
        Vehicle.objects
        .filter(is_deleted=False)
        .select_related("carrier")
        .prefetch_related(
            "tanker_compartments",
            "vehicle_memberships",
            "documents",
        )
    )

#====================
#     MEMBERSHIP
#====================


def list_vehicle_membership_requests(
) -> QuerySet[VehicleMembershipRequest]:
    return (
        VehicleMembershipRequest.objects
        .filter(is_deleted=False)
        .select_related(
            "vehicle",
            "vehicle__carrier",
        )
    )



def list_active_fleet_vehicles() -> QuerySet[Vehicle]:
    return (
        Vehicle.objects
        .filter(
            is_deleted=False,
            vehicle_memberships__is_deleted=False,
            vehicle_memberships__status=VehicleMembershipStatus.ACTIVE,
            vehicle_memberships__exit_date__isnull=True,
        )
        .select_related("carrier")
        .prefetch_related(
            "tanker_compartments",
            "vehicle_memberships",
            "documents",
        )
        .distinct()
    )

#====================
#     INSPECTIONS
#====================


# _get_inspection_criterion_or_error
# Retrieves an active inspection criterion by its identifier.
def _get_inspection_criterion_or_error(*,criterion_id,) -> InspectionCriterion:
    """
    Return an active inspection criterion.
    """
    criterion = InspectionCriterion.objects.filter(
        id=criterion_id,
        is_deleted=False,
        is_active=True,
    ).first()

    if criterion is None:
        raise ValidationError(
            {
                "criterion_id": (
                    "No active inspection criterion was found "
                    "with this identifier."
                )
            }
        )

    return criterion


def list_inspections_with_results() -> QuerySet[Inspection]:
    return (
        Inspection.objects
        .filter(is_deleted=False)
        .select_related(
            "vehicle",
            "inspection_version",
        )
        .prefetch_related(
            "criterion_results__criterion__section__chapter__inspection_version",
        )
    )


#====================
#     DEFECTS
#====================



def list_defects_with_source_and_resolution() -> QuerySet[Defect]:
    return (
        Defect.objects
        .filter(is_deleted=False)
        .select_related(
            "vehicle",
            "source_inspection",
            "source_inspection_criterion_result",
        )
      
    )



# ==================================
#  NextTripEligibilityEvaluation
# ==================================




def list_next_trip_eligibility_evaluations(
) -> QuerySet[NextTripEligibilityEvaluation]:
    return (
        NextTripEligibilityEvaluation.objects
        .filter(is_deleted=False)
        .select_related("vehicle")
        .prefetch_related("evaluation_reasons")
    )



# ==================================
#  VehicleAvailabilityEvaluation
# ==================================




def list_vehicle_availability_evaluations(
) -> QuerySet[VehicleAvailabilityEvaluation]:
    return (
        VehicleAvailabilityEvaluation.objects
        .filter(is_deleted=False)
        .select_related("vehicle")
        .prefetch_related("evaluation_reasons")
    )
