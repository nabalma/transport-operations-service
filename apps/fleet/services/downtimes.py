from apps.fleet.constants import DowntimeStatus, InspectionCriterionResultValue
from apps.fleet.models import Downtime, Vehicle,Defect,DowntimeCause,InspectionCriterionResult
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone



from apps.fleet.services.membership import ensure_vehicle_has_active_membership
from apps.fleet.services.vehicles import ensure_vehicle_is_active
from rest_framework.exceptions import ValidationError

# -------------------------------------------------------------------
# _downtime_has_defect
# Indique si un défaut est déjà enregistré comme cause
# de cette immobilisation.
# -------------------------------------------------------------------
def _downtime_has_defect(
    *,
    downtime: Downtime,
    defect: Defect,
) -> bool:
    """
    Retourne True si le défaut est déjà associé
    à cette immobilisation.
    """

    return downtime.causes.filter(
        defect=defect,
        is_deleted=False,
    ).exists()


# -------------------------------------------------------------------
# _ensure_downtime_does_not_have_defect
# Empêche d’ajouter deux fois le même défaut comme cause
# d’une même immobilisation.
# -------------------------------------------------------------------
def _ensure_downtime_does_not_have_defect(
    *,
    downtime: Downtime,
    defect: Defect,
) -> None:
    """
    Vérifie que le défaut n’est pas déjà associé
    à cette immobilisation.
    """

    if _downtime_has_defect(
        downtime=downtime,
        defect=defect,
    ):
        raise ValidationError(
            {
                "defect": (
                    "Ce défaut est déjà enregistré comme cause "
                    "de cette immobilisation."
                )
            }
        )





# -------------------------------------------------------------------
# _ensure_downtime_accepts_causes
# Vérifie qu’une immobilisation peut encore recevoir de nouvelles causes.
# -------------------------------------------------------------------
def _ensure_downtime_accepts_causes(
    *,
    downtime: Downtime,
) -> None:
    """
    Autorise l’ajout de causes uniquement sur une immobilisation
    active et non supprimée.
    """

    if downtime.is_deleted:
        raise ValidationError(
            {
                "downtime": (
                    "Une immobilisation supprimée ne peut pas recevoir "
                    "de nouvelle cause."
                )
            }
        )

    if downtime.status != DowntimeStatus.ACTIVE:
        raise ValidationError(
            {
                "status": (
                    "Seule une immobilisation active peut recevoir "
                    "de nouvelles causes."
                )
            }
        )

# -------------------------------------------------------------------
# _vehicle_has_active_downtime
# Indique si le véhicule possède déjà une immobilisation active.
# -------------------------------------------------------------------
def _vehicle_has_active_downtime(
    *,
    vehicle: Vehicle,
) -> bool:
    """
    Retourne True si le véhicule possède une immobilisation
    active et non supprimée.
    """

    return Downtime.objects.filter(
        vehicle=vehicle,
        status=DowntimeStatus.ACTIVE,
        end_date__isnull=True,
        is_deleted=False,
    ).exists()


# -------------------------------------------------------------------
# _ensure_vehicle_has_no_active_downtime
# Empêche la création de plusieurs immobilisations actives
# pour un même véhicule.
# -------------------------------------------------------------------
def _ensure_vehicle_has_no_active_downtime(
    *,
    vehicle: Vehicle,
) -> None:
    """
    Vérifie que le véhicule ne possède pas déjà
    une immobilisation active.
    """

    if _vehicle_has_active_downtime(
        vehicle=vehicle,
    ):
        raise ValidationError(
            {
                "vehicle": (
                    "Ce véhicule possède déjà une immobilisation active."
                )
            }
        )


# -------------------------------------------------------------------
# _get_active_downtime
# Retourne l’immobilisation active d’un véhicule, si elle existe.
# -------------------------------------------------------------------
def _get_active_downtime(
    *,
    vehicle: Vehicle,
) -> Downtime | None:
    """
    Retourne l’immobilisation active et non supprimée du véhicule.
    """

    return (
        Downtime.objects
        .filter(
            vehicle=vehicle,
            status=DowntimeStatus.ACTIVE,
            end_date__isnull=True,
            is_deleted=False,
        )
        .first()
    )


def _downtime_has_criterion_result(
    *,
    downtime: Downtime,
    criterion_result: InspectionCriterionResult,
) -> bool:
    """
    Indique si ce résultat d’inspection est déjà une cause
    de l’immobilisation.
    """

    return downtime.causes.filter(
        inspection_criterion_result=criterion_result,
        is_deleted=False,
    ).exists()


def _ensure_downtime_does_not_have_criterion_result(
    *,
    downtime: Downtime,
    criterion_result: InspectionCriterionResult,
) -> None:
    """
    Empêche d’ajouter deux fois le même résultat d’inspection.
    """

    if _downtime_has_criterion_result(
        downtime=downtime,
        criterion_result=criterion_result,
    ):
        raise ValidationError(
            {
                "inspection_criterion_result": (
                    "Ce résultat d’inspection est déjà enregistré "
                    "comme cause de cette immobilisation."
                )
            }
        )


# -------------------------------------------------------------------
# _ensure_downtime_cause_is_valid
# Vérifie qu’une cause d’immobilisation contient suffisamment
# d’informations.
# -------------------------------------------------------------------
def _ensure_downtime_cause_is_valid(
    *,
    inspection_criterion_result: InspectionCriterionResult | None,
    defect: Defect | None,
    reason: str,
) -> None:
    """
    Vérifie qu’une cause automatique ou manuelle est correctement définie.
    """

    is_manual = (
        inspection_criterion_result is None
        and defect is None
    )

    if is_manual and not reason.strip():
        raise ValidationError(
            {
                "reason": (
                    "Une raison est obligatoire pour une cause manuelle."
                )
            }
        )

    if defect is not None and inspection_criterion_result is None:
        raise ValidationError(
            {
                "defect": (
                    "Un défaut issu d’une inspection doit être rattaché "
                    "au résultat d’inspection correspondant."
                )
            }
        )

# -------------------------------------------------------------------
# add_downtime_cause
# Ajoute une cause à une immobilisation active.
# -------------------------------------------------------------------
@transaction.atomic
def add_downtime_cause(
    *,
    downtime: Downtime,
    user,
    defect: Defect | None = None,
    reason: str = "",
    inspection_criterion_result: InspectionCriterionResult | None = None,
) -> DowntimeCause:
    """
    Ajoute une cause à une immobilisation active.

    Une cause peut provenir d’un résultat d’inspection
    ou être saisie manuellement.
    """

    _ensure_downtime_accepts_causes(
        downtime=downtime,
    )

    _ensure_downtime_cause_is_valid(
        inspection_criterion_result=inspection_criterion_result,
        defect=defect,
        reason=reason,
    )

    if inspection_criterion_result is not None:
        _ensure_downtime_does_not_have_criterion_result(
            downtime=downtime,
            criterion_result=inspection_criterion_result,
        )

    if defect is not None:
        _ensure_downtime_does_not_have_defect(
            downtime=downtime,
            defect=defect,
        )

    cause = DowntimeCause(
        downtime=downtime,
        inspection_criterion_result=inspection_criterion_result,
        defect=defect,
        reason=reason.strip(),
        created_by=user,
        updated_by=user,
    )

    try:
        cause.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict) from exc

    cause.save()

    return cause


# -------------------------------------------------------------------
# create_manual_downtime
# Crée une immobilisation manuelle avec sa première cause.
# -------------------------------------------------------------------
@transaction.atomic
def create_manual_downtime(
    *,
    vehicle: Vehicle,
    reason: str,
    user,
    start_date=None,
) -> Downtime:
    """
    Immobilise manuellement un véhicule.

    Une première cause manuelle est créée dans la même transaction.
    """

    ensure_vehicle_has_active_membership(
        vehicle=vehicle,
    )

    ensure_vehicle_is_active(
        vehicle=vehicle,
    )

    _ensure_vehicle_has_no_active_downtime(
        vehicle=vehicle,
    )

    reason = reason.strip()

    _ensure_downtime_cause_is_valid(
    inspection_criterion_result=None,
    defect=None,
    reason=reason,
)


    downtime = Downtime(
        vehicle=vehicle,
        status=DowntimeStatus.ACTIVE,
        start_date=start_date or timezone.now(),
        end_date=None,
        created_by=user,
        updated_by=user,
    )

    try:
        downtime.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict) from exc

    downtime.save()

    add_downtime_cause(
        downtime=downtime,
        defect=None,
        reason=reason,
        user=user,
    )

    return downtime


# -------------------------------------------------------------------
# _get_or_create_active_downtime
# Récupère l’immobilisation active du véhicule ou en crée une.
# -------------------------------------------------------------------
def _get_or_create_active_downtime(
    *,
    vehicle: Vehicle,
    user,
) -> Downtime:
    """
    Retourne l’immobilisation active du véhicule.

    Si aucune immobilisation active n’existe, une nouvelle
    immobilisation est créée.
    """

    downtime = _get_active_downtime(
        vehicle=vehicle,
    )

    if downtime is not None:
        return downtime

    downtime = Downtime(
        vehicle=vehicle,
        status=DowntimeStatus.ACTIVE,
        start_date=timezone.now(),
        end_date=None,
        created_by=user,
        updated_by=user,
    )

    try:
        downtime.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict) from exc

    downtime.save()

    return downtime



# -------------------------------------------------------------------
# _ensure_criterion_result_triggers_downtime
# Vérifie qu’un résultat d’inspection doit réellement
# entraîner une immobilisation.
# -------------------------------------------------------------------
def _ensure_criterion_result_triggers_downtime(
    *,
    criterion_result: InspectionCriterionResult,
) -> None:
    """
    Autorise l’immobilisation uniquement lorsqu’un critère bloquant
    possède un résultat FAIL.
    """

    if criterion_result.result != InspectionCriterionResultValue.FAIL:
        raise ValidationError(
            {
                "inspection_criterion_result": (
                    "Seul un résultat d’inspection en échec peut "
                    "entraîner une immobilisation."
                )
            }
        )

    if not criterion_result.criterion.is_blocking_if_failed:
        raise ValidationError(
            {
                "inspection_criterion_result": (
                    "Ce critère d’inspection n’est pas bloquant "
                    "en cas d’échec."
                )
            }
        )





# -------------------------------------------------------------------
# create_or_update_downtime_from_blocking_criterion_result
# Crée ou enrichit l’immobilisation provoquée par l’échec
# d’un critère bloquant.
# -------------------------------------------------------------------
@transaction.atomic
def create_or_update_downtime_from_blocking_criterion_result(
    *,
    criterion_result: InspectionCriterionResult,
    user,
    defect: Defect | None = None,
) -> DowntimeCause:
    """
    Crée ou récupère l’immobilisation active du véhicule inspecté,
    puis ajoute une nouvelle cause d’immobilisation.

    Le résultat doit être FAIL et le critère doit être bloquant.
    Le défaut est facultatif, car creates_defect_if_failed et
    is_blocking_if_failed sont deux règles indépendantes.
    """

    _ensure_criterion_result_triggers_downtime(
        criterion_result=criterion_result,
    )

    downtime = _get_or_create_active_downtime(
        vehicle=criterion_result.inspection.vehicle,
        user=user,
    )

    cause = add_downtime_cause(
        downtime=downtime,
        inspection_criterion_result=criterion_result,
        defect=defect,
        reason="",
        user=user,
    )

    return cause