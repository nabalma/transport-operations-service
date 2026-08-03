from uuid import UUID
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.fleet.constants import DowntimeStatus, ReturnToServiceDecision
from apps.fleet.models import Downtime, ReturnToService
from apps.fleet.services.downtimes import (
    ensure_downtime_accepts_return_to_service,
    ensure_downtime_has_no_pending_return_to_service,
    ensure_downtime_has_no_unresolved_causes,
)


@transaction.atomic
def create_return_to_service(
    *,
    downtime: Downtime,
    source_type: str,
    proposed_by_system: bool,
    user,
    source_id: UUID | None = None,
) -> ReturnToService:
    """
    Crée une demande de remise en service pour une immobilisation.

    L'immobilisation doit être active, toutes ses causes doivent être
    résolues et aucune autre demande ne doit être en attente.
    """

    downtime = (
        Downtime.objects
        .select_for_update()
        .select_related("vehicle")
        .get(pk=downtime.pk)
    )

    ensure_downtime_accepts_return_to_service(
        downtime=downtime,
    )

    ensure_downtime_has_no_unresolved_causes(
        downtime=downtime,
    )

    ensure_downtime_has_no_pending_return_to_service(
        downtime=downtime,
    )

    return_to_service = ReturnToService(
        vehicle=downtime.vehicle,
        downtime=downtime,
        source_type=source_type,
        source_id=source_id,
        proposed_by_system=proposed_by_system,
        decision=ReturnToServiceDecision.PENDING,
        created_by=user,
        updated_by=user,
    )

    try:
        return_to_service.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict) from exc

    return_to_service.save()

    return return_to_service


# -------------------------------------------------------------------
# _ensure_return_to_service_can_be_decided
# Vérifie qu'une demande de remise en service peut recevoir
# une décision.
# -------------------------------------------------------------------
def _ensure_return_to_service_can_be_decided(
    *,
    return_to_service: ReturnToService,
) -> None:
    """
    Autorise une décision uniquement si la demande est
    en attente et non supprimée.
    """

    if return_to_service.is_deleted:
        raise ValidationError(
            {
                "return_to_service": (
                    "Cette demande de remise en service est supprimée."
                )
            }
        )

    if (
        return_to_service.decision
        != ReturnToServiceDecision.PENDING
    ):
        raise ValidationError(
            {
                "decision": (
                    "Cette demande de remise en service a déjà été traitée."
                )
            }
        )

# -------------------------------------------------------------------
# _ensure_return_to_service_decision_is_valid
# Vérifie que la décision demandée est valide.
# -------------------------------------------------------------------
def _ensure_return_to_service_decision_is_valid(
    *,
    decision: str,
    comment: str | None,
) -> None:
    """
    Autorise uniquement APPROVED ou REJECTED.

    Un commentaire est obligatoire lorsque la remise
    en service est rejetée.
    """

    if decision not in (
        ReturnToServiceDecision.APPROVED,
        ReturnToServiceDecision.REJECTED,
    ):
        raise ValidationError(
            {
                "decision": (
                    "La décision doit être APPROVED ou REJECTED."
                )
            }
        )

    if (
        decision == ReturnToServiceDecision.REJECTED
        and not (comment or "").strip()
    ):
        raise ValidationError(
            {
                "comment": (
                    "Un commentaire est obligatoire lorsque "
                    "la remise en service est rejetée."
                )
            }
        )

# -------------------------------------------------------------------
# _apply_return_to_service_decision
# Applique une décision finale à une demande de remise en service.
# -------------------------------------------------------------------
def _apply_return_to_service_decision(
    *,
    return_to_service: ReturnToService,
    decision: str,
    comment: str | None,
    user,
) -> ReturnToService:
    """
    Enregistre la décision finale sur la demande de remise en service.
    """

    return_to_service.decision = decision
    return_to_service.decided_by = user
    return_to_service.decided_at = timezone.now()
    return_to_service.comment = (
        comment.strip()
        if comment
        else None
    )
    return_to_service.updated_by = user

    return_to_service.save(
        update_fields=[
            "decision",
            "decided_by",
            "decided_at",
            "comment",
            "updated_by",
            "updated_at",
        ]
    )

    return return_to_service



# -------------------------------------------------------------------
# _end_downtime
# Termine une immobilisation après approbation
# de la remise en service.
# -------------------------------------------------------------------
def _end_downtime(
    *,
    downtime: Downtime,
    user,
) -> Downtime:
    """
    Passe l’immobilisation au statut ENDED
    et renseigne sa date de fin.
    """

    downtime.status = DowntimeStatus.ENDED
    downtime.end_date = timezone.now()
    downtime.updated_by = user

    downtime.save(
        update_fields=[
            "status",
            "end_date",
            "updated_by",
            "updated_at",
        ]
    )

    return downtime



# -------------------------------------------------------------------
# decide_return_to_service
# Approuve ou rejette une demande de remise en service.
# -------------------------------------------------------------------
@transaction.atomic
def _decide_return_to_service(
    *,
    return_to_service: ReturnToService,
    decision: str,
    user,
    comment: str | None = None,
) -> ReturnToService:
    """
    Approuve ou rejette une demande de remise en service.
    """

    return_to_service = (
        ReturnToService.objects
        .select_for_update()
        .get(pk=return_to_service.pk)
    )

    _ensure_return_to_service_can_be_decided(
        return_to_service=return_to_service,
    )

    _ensure_return_to_service_decision_is_valid(
        decision=decision,
        comment=comment,
    )

    if return_to_service.downtime_id is None:
        raise ValidationError(
            {
                "downtime": (
                    "Cette demande de remise en service n’est liée "
                    "à aucune immobilisation."
                )
            }
        )

    downtime = (
        Downtime.objects
        .select_for_update()
        .get(pk=return_to_service.downtime_id)
    )

    _apply_return_to_service_decision(
        return_to_service=return_to_service,
        decision=decision,
        comment=comment,
        user=user,
    )

    if decision == ReturnToServiceDecision.APPROVED:
        _end_downtime(
            downtime=downtime,
            user=user,
        )

    return return_to_service



# -------------------------------------------------------------------
# approve_return_to_service
# Approuve une demande de remise en service.
# -------------------------------------------------------------------
def approve_return_to_service(
    *,
    return_to_service: ReturnToService,
    user,
    comment: str | None = None,
) -> ReturnToService:
    """
    Approuve une demande de remise en service.

    L’approbation termine l’immobilisation liée.
    """

    return _decide_return_to_service(
        return_to_service=return_to_service,
        decision=ReturnToServiceDecision.APPROVED,
        comment=comment,
        user=user,
    )

# -------------------------------------------------------------------
# reject_return_to_service
# Rejette une demande de remise en service.
# -------------------------------------------------------------------
def reject_return_to_service(
    *,
    return_to_service: ReturnToService,
    user,
    comment: str,
) -> ReturnToService:
    """
    Rejette une demande de remise en service.

    Le rejet laisse l’immobilisation liée en statut ACTIVE.
    """

    return _decide_return_to_service(
        return_to_service=return_to_service,
        decision=ReturnToServiceDecision.REJECTED,
        comment=comment,
        user=user,
    )