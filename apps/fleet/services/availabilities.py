from apps.fleet.constants import (
    VehicleAvailabilityReasonType,
    VehicleAvailabilityResult,
    VehicleStatus,
)
from apps.fleet.models import Vehicle
from apps.fleet.models.availabilities import VehicleAvailabilityEvaluation, VehicleAvailabilityEvaluationReason
from apps.fleet.services.downtimes import (
    get_active_downtime,

)
from apps.fleet.services.membership import (
    vehicle_has_active_membership,
)
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.utils import timezone


# -------------------------------------------------------------------
# build_vehicle_availability_reasons
# Construit les raisons expliquant le résultat de disponibilité
# calculé pour un véhicule.
# -------------------------------------------------------------------
def build_vehicle_availability_reasons(
    *,
    vehicle: Vehicle,
) -> list[dict]:
    """
    Retourne la liste des raisons rendant éventuellement
    le véhicule indisponible.
    """

    reasons: list[dict] = []

    if vehicle.is_deleted or vehicle.status != VehicleStatus.ACTIVE:
        reasons.append(
            {
                "reason_type": (
                    VehicleAvailabilityReasonType.VEHICLE_INACTIVE
                ),
                "message": (
                    "Le véhicule est supprimé ou n'est pas actif."
                ),
                "source_id": vehicle.id,
            }
        )

    if not vehicle_has_active_membership(
        vehicle=vehicle,
    ):
        reasons.append(
            {
                "reason_type": (
                    VehicleAvailabilityReasonType.NO_ACTIVE_MEMBERSHIP
                ),
                "message": (
                    "Le véhicule ne possède aucune appartenance active "
                    "à la flotte."
                ),
                "source_id": vehicle.id,
            }
        )

    active_downtime = get_active_downtime(
        vehicle=vehicle,
    )

    if active_downtime is not None:
        reasons.append(
            {
                "reason_type": (
                    VehicleAvailabilityReasonType.ACTIVE_DOWNTIME
                ),
                "message": (
                    "Le véhicule possède une immobilisation active."
                ),
                "source_id": active_downtime.id,
            }
        )

    return reasons


# -------------------------------------------------------------------
# evaluate_vehicle_availability
# Calcule et enregistre une nouvelle évaluation de disponibilité
# ainsi que les raisons expliquant le résultat.
# -------------------------------------------------------------------
@transaction.atomic
def evaluate_vehicle_availability(
    *,
    vehicle: Vehicle,
    user,
) -> VehicleAvailabilityEvaluation:
    """
    Calcule et enregistre une évaluation de disponibilité,
    ainsi que les raisons expliquant le résultat.
    """

    reasons = build_vehicle_availability_reasons(
        vehicle=vehicle,
    )

    calculated_result = (
        VehicleAvailabilityResult.NOT_AVAILABLE
        if reasons
        else VehicleAvailabilityResult.AVAILABLE
    )

    evaluation = VehicleAvailabilityEvaluation(
        vehicle=vehicle,
        calculated_result=calculated_result,
        final_result=calculated_result,
        created_by=user,
        updated_by=user,
    )

    try:
        evaluation.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict) from exc

    evaluation.save()

    create_vehicle_availability_reasons(
        evaluation=evaluation,
        reasons=reasons,
        user=user,
    )

    return evaluation


# -------------------------------------------------------------------
# create_vehicle_availability_reasons
# Crée les raisons détaillées associées à une évaluation
# de disponibilité déjà enregistrée.
# -------------------------------------------------------------------
def create_vehicle_availability_reasons(
    *,
    evaluation: VehicleAvailabilityEvaluation,
    reasons: list[dict],
    user,
) -> list[VehicleAvailabilityEvaluationReason]:
    """
    Crée et retourne les raisons associées à l’évaluation.
    """

    evaluation_reasons = [
        VehicleAvailabilityEvaluationReason(
            evaluation=evaluation,
            reason_type=reason["reason_type"],
            message=reason["message"],
            source_id=reason.get("source_id"),
            created_by=user,
            updated_by=user,
        )
        for reason in reasons
    ]

    VehicleAvailabilityEvaluationReason.objects.bulk_create(
        evaluation_reasons,
    )

    return evaluation_reasons


# -------------------------------------------------------------------
# _ensure_availability_validation_is_valid
# Vérifie qu’une validation humaine est cohérente avec
# le résultat calculé par le système.
# -------------------------------------------------------------------
def _ensure_availability_validation_is_valid(
    *,
    evaluation: VehicleAvailabilityEvaluation,
    final_result: str,
    validation_comment: str | None,
) -> None:
    """
    Exige une justification lorsque le résultat final
    diffère du résultat calculé.
    """

    if final_result not in VehicleAvailabilityResult.values:
        raise ValidationError(
            {
                "final_result": (
                    "Le résultat final de disponibilité est invalide."
                )
            }
        )

    if (
        final_result != evaluation.calculated_result
        and not (validation_comment or "").strip()
    ):
        raise ValidationError(
            {
                "validation_comment": (
                    "Un commentaire est obligatoire lorsque le résultat final "
                    "diffère du résultat calculé."
                )
            }
        )


# -------------------------------------------------------------------
# _ensure_availability_evaluation_can_be_validated
# Empêche de valider plusieurs fois la même évaluation
# de disponibilité.
# -------------------------------------------------------------------
def _ensure_availability_evaluation_can_be_validated(
    *,
    evaluation: VehicleAvailabilityEvaluation,
) -> None:
    """
    Autorise la validation uniquement si l’évaluation
    n’a pas encore été validée.
    """

    if evaluation.is_deleted:
        raise ValidationError(
            {
                "evaluation": (
                    "Une évaluation supprimée ne peut pas être validée."
                )
            }
        )

    if evaluation.validated_at is not None:
        raise ValidationError(
            {
                "evaluation": (
                    "Cette évaluation de disponibilité a déjà été validée."
                )
            }
        )

    

# -------------------------------------------------------------------
# validate_vehicle_availability_evaluation
# Confirme ou modifie le résultat final d’une évaluation
# de disponibilité.
# -------------------------------------------------------------------
@transaction.atomic
def validate_vehicle_availability_evaluation(
    *,
    evaluation: VehicleAvailabilityEvaluation,
    final_result: str,
    user,
    validation_comment: str | None = None,
) -> VehicleAvailabilityEvaluation:
    """
    Enregistre la décision humaine sur une évaluation
    de disponibilité.
    """

    _ensure_availability_evaluation_can_be_validated(
    evaluation=evaluation,
    )
    
    _ensure_availability_validation_is_valid(
        evaluation=evaluation,
        final_result=final_result,
        validation_comment=validation_comment,
    )

    evaluation.final_result = final_result
    evaluation.validated_by = user
    evaluation.validated_at = timezone.now()
    evaluation.validation_comment = (
        validation_comment.strip()
        if validation_comment
        else None
    )
    evaluation.updated_by = user

    evaluation.save(
        update_fields=[
            "final_result",
            "validated_by",
            "validated_at",
            "validation_comment",
            "updated_by",
            "updated_at",
        ]
    )

    return evaluation