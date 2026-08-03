from uuid import UUID

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.fleet.constants import ReturnToServiceDecision
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