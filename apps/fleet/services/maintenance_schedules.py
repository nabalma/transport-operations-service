
from apps.fleet.constants import MaintenanceScheduleStatus, MaintenanceWorkOrderKind


from apps.fleet.services.maintenance_work_orders import create_maintenance_work_order
from apps.fleet.services.membership import ensure_vehicle_has_active_membership
from apps.fleet.services.vehicles import ensure_vehicle_is_active
from rest_framework.exceptions import ValidationError

from apps.fleet.models import MaintenanceWorkOrder, MaintenanceSchedule, Vehicle,MaintenancePolicy
from datetime import datetime

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone


# _ensure_maintenance_policy_can_be_scheduled
# Vérifie qu’une politique peut être utilisée pour une planification.
def _ensure_maintenance_policy_can_be_scheduled(
    *,
    policy: MaintenancePolicy,
) -> None:
    """
    Empêche l’utilisation d’une politique supprimée ou inactive.
    """

    if policy.is_deleted:
        raise ValidationError(
            {
                "policy": (
                    "Une politique supprimée ne peut pas être utilisée "
                    "pour une planification."
                )
            }
        )

    if not policy.is_active:
        raise ValidationError(
            {
                "policy": (
                    "Une politique inactive ne peut pas être utilisée "
                    "pour une planification."
                )
            }
        )


# _active_schedule_exists
# Indique si une planification active existe déjà.
def _active_schedule_exists(
    *,
    vehicle: Vehicle,
    policy: MaintenancePolicy,
) -> bool:
    """
    Retourne True si une planification active et non supprimée existe.
    """

    return MaintenanceSchedule.objects.filter(
        vehicle=vehicle,
        policy=policy,
        status=MaintenanceScheduleStatus.ACTIVE,
        is_deleted=False,
    ).exists()



# _ensure_no_active_schedule_exists
# Vérifie qu’aucune planification active n’existe déjà.
def _ensure_no_active_schedule_exists(
    *,
    vehicle: Vehicle,
    policy: MaintenancePolicy,
) -> None:
    """
    Empêche la création de plusieurs planifications actives
    pour le même véhicule et la même politique.
    """

    if _active_schedule_exists(
        vehicle=vehicle,
        policy=policy,
    ):
        raise ValidationError(
            {
                "schedule": (
                    "Une planification active existe déjà pour ce véhicule "
                    "et cette politique."
                )
            }
        )


# _ensure_schedule_has_due_value
# Vérifie qu’une planification possède au moins une échéance.
def _ensure_schedule_has_due_value(
    *,
    due_at : datetime | None = None,
    due_mileage: int | None,
    due_engine_hours: int | None,
) -> None:
    """
    Exige au moins une échéance en date, kilométrage
    ou heures moteur.
    """

    if (
        due_at is None
        and due_mileage is None
        and due_engine_hours is None
    ):
        raise ValidationError(
            {
                "schedule": (
                    "Au moins une échéance doit être renseignée."
                )
            }
        )


# _ensure_schedule_due_values_match_policy
# Vérifie que les échéances correspondent exactement à la politique.
def _ensure_schedule_due_values_match_policy(
    *,
    policy: MaintenancePolicy,
    due_at : datetime | None = None,
    due_mileage: int | None,
    due_engine_hours: int | None,
) -> None:
    """
    Vérifie que chaque intervalle configuré dans la politique
    possède une échéance correspondante dans la planification.
    """

    if policy.interval_days is not None and due_at is None:
        raise ValidationError(
            {
                "due_at": (
                    "Une échéance calendaire est obligatoire pour "
                    "cette politique."
                )
            }
        )

    if policy.interval_days is None and due_at is not None:
        raise ValidationError(
            {
                "due_at": (
                    "Cette politique ne prévoit pas d’échéance calendaire."
                )
            }
        )

    if policy.interval_mileage is not None and due_mileage is None:
        raise ValidationError(
            {
                "due_mileage": (
                    "Une échéance kilométrique est obligatoire pour "
                    "cette politique."
                )
            }
        )

    if policy.interval_mileage is None and due_mileage is not None:
        raise ValidationError(
            {
                "due_mileage": (
                    "Cette politique ne prévoit pas d’échéance kilométrique."
                )
            }
        )

    if (
        policy.interval_engine_hours is not None
        and due_engine_hours is None
    ):
        raise ValidationError(
            {
                "due_engine_hours": (
                    "Une échéance en heures moteur est obligatoire pour "
                    "cette politique."
                )
            }
        )

    if (
        policy.interval_engine_hours is None
        and due_engine_hours is not None
    ):
        raise ValidationError(
            {
                "due_engine_hours": (
                    "Cette politique ne prévoit pas d’échéance "
                    "en heures moteur."
                )
            }
        )


# _ensure_schedule_due_values_are_positive
# Vérifie que les échéances numériques sont strictement positives.
def _ensure_schedule_due_values_are_positive(
    *,
    due_mileage: int | None,
    due_engine_hours: int | None,
) -> None:
    """
    Refuse les échéances kilométriques ou horaires nulles ou négatives.
    """

    if due_mileage is not None and due_mileage <= 0:
        raise ValidationError(
            {
                "due_mileage": (
                    "L’échéance kilométrique doit être strictement "
                    "supérieure à zéro."
                )
            }
        )

    if due_engine_hours is not None and due_engine_hours <= 0:
        raise ValidationError(
            {
                "due_engine_hours": (
                    "L’échéance en heures moteur doit être strictement "
                    "supérieure à zéro."
                )
            }
        )




# =====================================
# CRÉER UNE PLANIFICATION DE MAINTENANCE
# =====================================

# create_maintenance_schedule
# Crée une planification active pour un véhicule et une politique.
@transaction.atomic
def create_maintenance_schedule(
    *,
    vehicle: Vehicle,
    policy: MaintenancePolicy,
    user,
    due_at: datetime | None = None,
    due_mileage: int | None = None,
    due_engine_hours: int | None = None,
) -> MaintenanceSchedule:
    """
    Crée une planification de maintenance active.

    Le véhicule doit être actif et appartenir à la flotte.
    La politique doit être active et les échéances doivent lui correspondre.
    """

    ensure_vehicle_has_active_membership(
        vehicle=vehicle,
    )

    ensure_vehicle_is_active(
        vehicle=vehicle,
    )

    _ensure_maintenance_policy_can_be_scheduled(
        policy=policy,
    )

    _ensure_no_active_schedule_exists(
        vehicle=vehicle,
        policy=policy,
    )

    _ensure_schedule_has_due_value(
        due_at=due_at,
        due_mileage=due_mileage,
        due_engine_hours=due_engine_hours,
    )

    _ensure_schedule_due_values_match_policy(
        policy=policy,
        due_at=due_at,
        due_mileage=due_mileage,
        due_engine_hours=due_engine_hours,
    )

    _ensure_schedule_due_values_are_positive(
        due_mileage=due_mileage,
        due_engine_hours=due_engine_hours,
    )

    schedule = MaintenanceSchedule(
        vehicle=vehicle,
        policy=policy,
        status=MaintenanceScheduleStatus.ACTIVE,
        due_at=due_at,
        due_mileage=due_mileage,
        due_engine_hours=due_engine_hours,
        created_by=user,
        updated_by=user,
    )

    try:
        schedule.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict) from exc

    schedule.save()

    return schedule



# _ensure_schedule_can_be_cancelled
# Vérifie qu’une planification peut encore être annulée.
def _ensure_schedule_can_be_cancelled(
    *,
    schedule: MaintenanceSchedule,
) -> None:
    """
    Autorise l’annulation uniquement pour une planification active
    et non supprimée.
    """

    if schedule.is_deleted:
        raise ValidationError(
            {
                "schedule": (
                    "Une planification supprimée ne peut pas être annulée."
                )
            }
        )

    if schedule.status != MaintenanceScheduleStatus.ACTIVE:
        raise ValidationError(
            {
                "status": (
                    "Seule une planification active peut être annulée."
                )
            }
        )


# ==========================================
# ANNULER UNE PLANIFICATION DE MAINTENANCE
# ==========================================

# cancel_maintenance_schedule
# Annule une planification de maintenance encore active.
@transaction.atomic
def cancel_maintenance_schedule(
    *,
    schedule: MaintenanceSchedule,
    cancellation_reason: str,
    user,
) -> MaintenanceSchedule:
    """
    Annule une planification de maintenance active.

    Le motif d’annulation est obligatoire.
    """

    _ensure_schedule_can_be_cancelled(
        schedule=schedule,
    )

    cancellation_reason = cancellation_reason.strip()

    if not cancellation_reason:
        raise ValidationError(
            {
                "cancellation_reason": (
                    "Le motif d’annulation est obligatoire."
                )
            }
        )

    schedule.status = MaintenanceScheduleStatus.CANCELLED
    schedule.cancelled_at = timezone.now()
    schedule.cancellation_reason = cancellation_reason
    schedule.updated_by = user

    schedule.save(
        update_fields=[
            "status",
            "cancelled_at",
            "cancellation_reason",
            "updated_by",
            "updated_at",
        ]
    )

    return schedule


# _ensure_schedule_can_be_updated
# Vérifie qu’une planification peut encore être modifiée.
def _ensure_schedule_can_be_updated(
    *,
    schedule: MaintenanceSchedule,
) -> None:
    """
    Autorise la modification uniquement pour une planification active
    et non supprimée.
    """

    if schedule.is_deleted:
        raise ValidationError(
            {
                "schedule": (
                    "Une planification supprimée ne peut pas être modifiée."
                )
            }
        )

    if schedule.status != MaintenanceScheduleStatus.ACTIVE:
        raise ValidationError(
            {
                "status": (
                    "Seule une planification active peut être modifiée."
                )
            }
        )

# ==========================================
# MODIFIER UNE PLANIFICATION DE MAINTENANCE
# ==========================================

# update_maintenance_schedule
# Met à jour les échéances d’une planification encore active.
@transaction.atomic
def update_maintenance_schedule(
    *,
    schedule: MaintenanceSchedule,
    due_at: datetime | None,
    due_mileage: int | None,
    due_engine_hours: int | None,
    user,
) -> MaintenanceSchedule:
    """
    Met à jour les échéances d’une planification active.

    Le véhicule, la politique et le statut restent immuables.
    """

    _ensure_schedule_can_be_updated(
        schedule=schedule,
    )

    _ensure_schedule_has_due_value(
        due_at=due_at,
        due_mileage=due_mileage,
        due_engine_hours=due_engine_hours,
    )

    _ensure_schedule_due_values_match_policy(
        policy=schedule.policy,
        due_at=due_at,
        due_mileage=due_mileage,
        due_engine_hours=due_engine_hours,
    )

    _ensure_schedule_due_values_are_positive(
        due_mileage=due_mileage,
        due_engine_hours=due_engine_hours,
    )

    schedule.due_at = due_at
    schedule.due_mileage = due_mileage
    schedule.due_engine_hours = due_engine_hours
    schedule.updated_by = user

    try:
        schedule.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict) from exc

    schedule.save(
        update_fields=[
            "due_at",
            "due_mileage",
            "due_engine_hours",
            "updated_by",
            "updated_at",
        ]
    )

    return schedule



# _ensure_schedule_can_be_fulfilled
# Vérifie qu’une planification peut être déclarée réalisée.
def _ensure_schedule_can_be_fulfilled(
    *,
    schedule: MaintenanceSchedule,
) -> None:
    """
    Autorise la clôture uniquement pour une planification active
    et non supprimée.
    """

    if schedule.is_deleted:
        raise ValidationError(
            {
                "schedule": (
                    "Une planification supprimée ne peut pas être réalisée."
                )
            }
        )

    if schedule.status != MaintenanceScheduleStatus.ACTIVE:
        raise ValidationError(
            {
                "status": (
                    "Seule une planification active peut être réalisée."
                )
            }
        )


# ==========================================
# RÉALISER UNE PLANIFICATION DE MAINTENANCE
# ==========================================

# fulfill_maintenance_schedule
# Déclare une planification active comme réalisée.
@transaction.atomic
def fulfill_maintenance_schedule(
    *,
    schedule: MaintenanceSchedule,
    user,
) -> MaintenanceSchedule:
    """
    Marque une planification de maintenance comme réalisée.

    La planification doit être active et non supprimée.
    """

    _ensure_schedule_can_be_fulfilled(
        schedule=schedule,
    )

    schedule.status = MaintenanceScheduleStatus.FULFILLED
    schedule.fulfilled_at = timezone.now()
    schedule.updated_by = user

    schedule.save(
        update_fields=[
            "status",
            "fulfilled_at",
            "updated_by",
            "updated_at",
        ]
    )

    return schedule



# _ensure_schedule_can_be_deleted
# Vérifie qu'une planification peut être supprimée logiquement.
def _ensure_schedule_can_be_deleted(
    *,
    schedule: MaintenanceSchedule,
) -> None:
    """
    Autorise la suppression uniquement pour une planification active.
    """

    if schedule.is_deleted:
        raise ValidationError(
            {
                "schedule": (
                    "Cette planification est déjà supprimée."
                )
            }
        )

    if schedule.status != MaintenanceScheduleStatus.ACTIVE:
        raise ValidationError(
            {
                "status": (
                    "Seule une planification active peut être supprimée."
                )
            }
        )

# ==========================================
# SUPPRIMER UNE PLANIFICATION DE MAINTENANCE
# ==========================================

# delete_maintenance_schedule
# Supprime logiquement une planification encore active.
@transaction.atomic
def delete_maintenance_schedule(
    *,
    schedule: MaintenanceSchedule,
    user,
    reason: str = "",
) -> MaintenanceSchedule:
    """
    Supprime logiquement une planification de maintenance.

    Seule une planification active peut être supprimée.
    """

    _ensure_schedule_can_be_deleted(
        schedule=schedule,
    )

    schedule.is_deleted = True
    schedule.deleted_at = timezone.now()
    schedule.deleted_by = user
    schedule.deleted_reason = reason.strip() or None
    schedule.updated_by = user

    schedule.save(
        update_fields=[
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "deleted_reason",
            "updated_by",
            "updated_at",
        ]
    )

    return schedule



# _ensure_schedule_can_generate_work_order
# Vérifie qu’une planification peut générer un ordre préventif.
def _ensure_schedule_can_generate_work_order(
    *,
    schedule: MaintenanceSchedule,
) -> None:
    """
    Autorise la génération uniquement depuis une planification
    active et non supprimée.
    """

    if schedule.is_deleted:
        raise ValidationError(
            {
                "schedule": (
                    "Une planification supprimée ne peut pas générer "
                    "un ordre de travail."
                )
            }
        )

    if schedule.status != MaintenanceScheduleStatus.ACTIVE:
        raise ValidationError(
            {
                "status": (
                    "Seule une planification active peut générer "
                    "un ordre de travail."
                )
            }
        )

# ==========================================
# GÉNÉRER UN ORDRE DE TRAVAIL PRÉVENTIF
# ==========================================

# generate_preventive_work_order
# Génère un ordre préventif depuis une planification active.
@transaction.atomic
def generate_preventive_work_order(
    *,
    schedule: MaintenanceSchedule,
    title: str,
    user,
    description: str = "",
    planned_start_at: datetime | None = None,
    planned_end_at: datetime | None = None,
)-> MaintenanceWorkOrder:
    """
    Crée un ordre de travail préventif depuis une planification active.
    """

    _ensure_schedule_can_generate_work_order(
        schedule=schedule,
    )

    return create_maintenance_work_order(
        vehicle=schedule.vehicle,
        kind=MaintenanceWorkOrderKind.PREVENTIVE,
        title=title,
        description=description,
        schedule=schedule,
        defect=None,
        planned_start_at=planned_start_at,
        planned_end_at=planned_end_at,
        user=user,
    )