from apps.fleet.constants import MaintenanceWorkOrderKind, MaintenanceWorkOrderStatus
from apps.fleet.models import Vehicle,MaintenanceSchedule,Defect,MaintenanceComponent,MaintenanceWorkOrder,MaintenanceWorkOrderItem
from django.db import transaction
from django.utils import timezone

from django.core.exceptions import ValidationError as DjangoValidationError
from datetime import datetime
from apps.fleet.services.membership import ensure_vehicle_has_active_membership
from rest_framework.exceptions import ValidationError

# =======================================
# CRÉER UN COMPOSANT DE MAINTENANCE
# =======================================

# create_maintenance_component
# Crée un composant dans le catalogue de maintenance.
# Le code est normalisé afin de rester stable et uniforme.
@transaction.atomic
def create_maintenance_component(
    *,
    code: str,
    name: str,
    scope: str,
    user,
    description: str = "",
    is_active: bool = True,
) -> MaintenanceComponent:
    """
    Crée et retourne un composant de maintenance.
    """

    component = MaintenanceComponent(
        code=code.strip().upper(),
        name=name.strip(),
        scope=scope,
        description=description.strip(),
        is_active=is_active,
        created_by=user,
        updated_by=user,
    )

    try:
        component.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict) from exc

    component.save()

    return component


# _ensure_work_order_accepts_items
# Vérifie qu’un ordre de travail peut encore recevoir des interventions.
def _ensure_work_order_items_are_editable(
    *,
    work_order: MaintenanceWorkOrder,
) -> None:
    """
    Empêche l’ajout d’interventions dans un ordre terminé,
    annulé ou supprimé.
    """

    if work_order.is_deleted:
        raise ValidationError(
            {
                "work_order": (
                    "Un ordre de travail supprimé ne peut pas recevoir "
                    "de nouvelles interventions."
                )
            }
        )

    if work_order.status != MaintenanceWorkOrderStatus.PLANNED:
        raise ValidationError(
            {
                "work_order": (
                    "Seul un ordre de travail planifié peut recevoir "
                    "de nouvelles interventions."
                )
            }
        )

# _ensure_component_can_be_used
# Vérifie qu’un composant peut être utilisé dans un ordre de travail.
def _ensure_component_can_be_used(
    *,
    component: MaintenanceComponent,
) -> None:
    """
    Empêche l’utilisation d’un composant supprimé ou inactif.
    """

    if component.is_deleted:
        raise ValidationError(
            {
                "component": (
                    "Un composant supprimé ne peut pas être utilisé "
                    "dans un ordre de travail."
                )
            }
        )

    if not component.is_active:
        raise ValidationError(
            {
                "component": (
                    "Un composant inactif ne peut pas être utilisé "
                    "dans un ordre de travail."
                )
            }
        )


@transaction.atomic
def create_maintenance_work_order_item(
    *,
    work_order: MaintenanceWorkOrder,
    component: MaintenanceComponent,
    user,
    description: str = "",
) -> MaintenanceWorkOrderItem:
    """
    Crée et retourne une intervention associée à un ordre de travail.
    """

    _ensure_work_order_items_are_editable(
        work_order=work_order,
    )

    _ensure_component_can_be_used(
        component=component,
    )

    item = MaintenanceWorkOrderItem(
        work_order=work_order,
        component=component,
        description=description.strip(),
        created_by=user,
        updated_by=user,
    )

    try:
        item.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict) from exc

    item.save()

    return item



# =========================================
# MODIFIER UNE INTERVENTION DE MAINTENANCE
# =========================================

# update_maintenance_work_order_item
# Met à jour une intervention appartenant à un ordre de travail planifié.
@transaction.atomic
def update_maintenance_work_order_item(
    *,
    item: MaintenanceWorkOrderItem,
    component: MaintenanceComponent,
    description: str,
    user,
) -> MaintenanceWorkOrderItem:
    """
    Met à jour une intervention d'un ordre de travail.
    """

    _ensure_work_order_items_are_editable(
        work_order=item.work_order,
    )

    _ensure_component_can_be_used(
        component=component,
    )

    item.component = component
    item.description = description.strip()
    item.updated_by = user

    try:
        item.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict) from exc

    item.save()

    return item



# ==========================================
# SUPPRIMER UNE INTERVENTION DE MAINTENANCE
# ==========================================

# delete_maintenance_work_order_item
# Supprime logiquement une intervention appartenant à un ordre planifié.
@transaction.atomic
def delete_maintenance_work_order_item(
    *,
    item: MaintenanceWorkOrderItem,
    user,
    reason: str = "",
) -> MaintenanceWorkOrderItem:
    """
    Supprime logiquement une intervention de maintenance.
    L'intervention ne peut être supprimée que si son ordre de travail
    est encore planifié.
    La suppression conserve l'objet en base et renseigne les informations
    de traçabilité associées.
    Args:
        item:
            Intervention de maintenance à supprimer.
        user:
            Utilisateur responsable de la suppression.
        reason:
            Motif facultatif de la suppression.
    Returns:
        MaintenanceWorkOrderItem:
            L'intervention supprimée logiquement.
    Raises:
        ValidationError:
            Si l'ordre de travail ne permet plus les modifications
            ou si l'intervention est déjà supprimée.
    """

    _ensure_work_order_items_are_editable(
        work_order=item.work_order,
    )

    if item.is_deleted:
        raise ValidationError(
            {
                "item": (
                    "Cette intervention de maintenance est déjà supprimée."
                )
            }
        )

    item.is_deleted = True
    item.deleted_at = timezone.now()
    item.deleted_by = user
    item.deleted_reason = reason.strip() or None
    item.updated_by = user

    item.save(
        update_fields=(
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "deleted_reason",
            "updated_by",
            "updated_at",
        )
    )

    return item


# -------------------------------------------------------------------
# Vérifie que l'origine de l'ordre correspond à son type.
# -------------------------------------------------------------------
def _ensure_work_order_origin_matches_kind(
    *,
    kind: str,
    schedule: MaintenanceSchedule | None,
    defect: Defect | None,
) -> None:
    """
    Vérifie que l'origine de l'ordre de travail est cohérente
    avec son type.
    """

    if kind == MaintenanceWorkOrderKind.PREVENTIVE:
        if schedule is None:
            raise ValidationError(
                {
                    "schedule": (
                        "Une maintenance préventive doit être liée "
                        "à une planification."
                    )
                }
            )

        if defect is not None:
            raise ValidationError(
                {
                    "defect": (
                        "Une maintenance préventive ne peut pas être "
                        "associée à un défaut."
                    )
                }
            )

    elif kind == MaintenanceWorkOrderKind.CORRECTIVE:
        if schedule is not None:
            raise ValidationError(
                {
                    "schedule": (
                        "Une maintenance corrective ne peut pas être "
                        "associée à une planification."
                    )
                }
            )

# _ensure_work_order_sources_match_vehicle
# Vérifie que la planification et le défaut concernent le même véhicule.
def _ensure_work_order_sources_match_vehicle(
    *,
    vehicle: Vehicle,
    schedule: MaintenanceSchedule | None,
    defect: Defect | None,
) -> None:
    """
    Vérifie la cohérence du véhicule entre l’ordre et ses sources.
    """

    if (
        schedule is not None
        and schedule.vehicle_id != vehicle.id
    ):
        raise ValidationError(
            {
                "schedule": (
                    "La planification doit concerner le même véhicule "
                    "que l’ordre de travail."
                )
            }
        )

    if (
        defect is not None
        and defect.vehicle_id != vehicle.id
    ):
        raise ValidationError(
            {
                "defect": (
                    "Le défaut doit concerner le même véhicule "
                    "que l’ordre de travail."
                )
            }
        )

 # _ensure_planned_dates_are_consistent
# Vérifie la cohérence des dates planifiées d'un ordre de travail.
def _ensure_planned_dates_are_consistent(
    *,
    planned_start_at: datetime | None,
    planned_end_at: datetime | None,
) -> None:
    """
    Vérifie que la date de fin planifiée n'est pas antérieure
    à la date de début planifiée.
    """

    if (
        planned_start_at is not None
        and planned_end_at is not None
        and planned_end_at < planned_start_at
    ):
        raise ValidationError(
            {
                "planned_end_at": (
                    "La date de fin planifiée doit être postérieure "
                    "ou égale à la date de début planifiée."
                )
            }
        )

       
# =====================================
# CRÉER UN ORDRE DE TRAVAIL MAINTENANCE
# =====================================

# create_maintenance_work_order
# Crée un ordre de travail de maintenance planifié.
@transaction.atomic
def create_maintenance_work_order(
    *,
    vehicle: Vehicle,
    kind: str,
    title: str,
    user,
    description: str = "",
    schedule: MaintenanceSchedule | None = None,
    defect: Defect | None = None,
    planned_start_at: datetime | None = None,
    planned_end_at: datetime | None = None,
) -> MaintenanceWorkOrder:
    """
    Crée un ordre de travail de maintenance.
    """
    ensure_vehicle_has_active_membership(
        vehicle=vehicle,
    )

    _ensure_work_order_origin_matches_kind(
        kind=kind,
        schedule=schedule,
        defect=defect,
    )
    _ensure_work_order_sources_match_vehicle(
    vehicle=vehicle,
    schedule=schedule,
    defect=defect,
    )

    _ensure_planned_dates_are_consistent(
    planned_start_at=planned_start_at,
    planned_end_at=planned_end_at,
    )

    work_order = MaintenanceWorkOrder(
        vehicle=vehicle,
        kind=kind,
        status=MaintenanceWorkOrderStatus.PLANNED,
        title=title.strip(),
        description=description.strip(),
        schedule=schedule,
        defect=defect,
        planned_start_at=planned_start_at,
        planned_end_at=planned_end_at,
        created_by=user,
        updated_by=user,
    )

    try:
        work_order.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict) from exc

    work_order.save()

    return work_order



# _ensure_work_order_allows_updates
# Vérifie qu’un ordre de travail peut encore être modifié.
def _ensure_work_order_allows_updates(
    *,
    work_order: MaintenanceWorkOrder,
) -> None:
    """
    Vérifie que l'ordre de travail peut encore être modifié.
    """

    if work_order.is_deleted:
        raise ValidationError(
            {
                "work_order": (
                    "Cet ordre de travail a été supprimé."
                )
            }
        )

    if work_order.status in (
        MaintenanceWorkOrderStatus.COMPLETED,
        MaintenanceWorkOrderStatus.CANCELLED,
    ):
        raise ValidationError(
            {
                "status": (
                    "Cet ordre de travail ne peut plus être modifié."
                )
            }
        )


# =====================================
# METTRE À JOUR UN ORDRE DE TRAVAIL
# =====================================

# update_maintenance_work_order
# Met à jour les informations modifiables d'un ordre de travail.
@transaction.atomic
def update_maintenance_work_order(
    *,
    work_order: MaintenanceWorkOrder,
    kind: str,
    title: str,
    description: str,
    schedule: MaintenanceSchedule | None,
    defect: Defect | None,
    planned_start_at: datetime | None,
    planned_end_at: datetime | None,
    user,
) -> MaintenanceWorkOrder:
    """
    Met à jour les informations modifiables d'un ordre de travail.

    Le véhicule et le statut ne peuvent pas être modifiés.
    """

    _ensure_work_order_allows_updates(
        work_order=work_order,
    )

    _ensure_work_order_origin_matches_kind(
        kind=kind,
        schedule=schedule,
        defect=defect,
    )
    _ensure_work_order_sources_match_vehicle(
    vehicle=work_order.vehicle,
    schedule=schedule,
    defect=defect,
    )

    _ensure_planned_dates_are_consistent(
    planned_start_at=planned_start_at,
    planned_end_at=planned_end_at,
)

    work_order.kind = kind
    work_order.title = title.strip()
    work_order.description = description.strip()
    work_order.schedule = schedule
    work_order.defect = defect
    work_order.planned_start_at = planned_start_at
    work_order.planned_end_at = planned_end_at
    work_order.updated_by = user

    try:
        work_order.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict) from exc

    work_order.save()

    return work_order



# _work_order_has_active_items
# Indique si un ordre de travail contient au moins une intervention active.
def _work_order_has_active_items(
    *,
    work_order: MaintenanceWorkOrder,
) -> bool:
    """
    Retourne True si l’ordre contient au moins un item non supprimé.
    """

    return work_order.items.filter(
        is_deleted=False,
    ).exists()


# _ensure_work_order_can_be_completed
# Vérifie qu’un ordre de travail peut être déclaré terminé.
def _ensure_work_order_can_be_completed(
    *,
    work_order: MaintenanceWorkOrder,
) -> None:
    """
    Vérifie qu’un ordre planifié contient au moins une intervention
    active avant sa clôture.
    """

    if work_order.is_deleted:
        raise ValidationError(
            {
                "work_order": (
                    "Un ordre de travail supprimé ne peut pas être terminé."
                )
            }
        )

    if work_order.status != MaintenanceWorkOrderStatus.PLANNED:
        raise ValidationError(
            {
                "status": (
                    "Seul un ordre de travail planifié peut être terminé."
                )
            }
        )

    has_active_item = _work_order_has_active_items( work_order=work_order)

    if not has_active_item:
        raise ValidationError(
            {
                "items": (
                    "Un ordre de travail doit contenir au moins une "
                    "intervention avant d’être terminé."
                )
            }
        )



# =====================================
# TERMINER UN ORDRE DE TRAVAIL
# =====================================

# complete_maintenance_work_order
# Déclare un ordre de travail comme terminé.
@transaction.atomic
def complete_maintenance_work_order(
    *,
    work_order: MaintenanceWorkOrder,
    completion_notes: str,
    user,
) -> MaintenanceWorkOrder:
    """
    Déclare un ordre de travail comme terminé.

    L'ordre doit être encore planifié et contenir au moins une
    intervention active.

    Args:
        work_order:
            Ordre de travail à terminer.

        completion_notes:
            Notes de clôture de l'intervention.

        user:
            Utilisateur responsable de la clôture.

    Returns:
        MaintenanceWorkOrder:
            L'ordre de travail terminé.

    Raises:
        ValidationError:
            Si l'ordre de travail ne peut pas être terminé.
    """

    _ensure_work_order_can_be_completed(
        work_order=work_order,
    )

    work_order.status = MaintenanceWorkOrderStatus.COMPLETED
    work_order.completed_at = timezone.now()
    work_order.completion_notes = completion_notes.strip()
    work_order.updated_by = user

    work_order.save(
        update_fields=[
            "status",
            "completed_at",
            "completion_notes",
            "updated_by",
            "updated_at",
        ]
    )

    return work_order



# _ensure_work_order_can_be_cancelled
# Vérifie qu’un ordre de travail peut encore être annulé.
def _ensure_work_order_can_be_cancelled(
    *,
    work_order: MaintenanceWorkOrder,
) -> None:
    """
    Autorise l’annulation uniquement pour un ordre planifié
    et non supprimé.
    """

    if work_order.is_deleted:
        raise ValidationError(
            {
                "work_order": (
                    "Un ordre de travail supprimé ne peut pas être annulé."
                )
            }
        )

    if work_order.status != MaintenanceWorkOrderStatus.PLANNED:
        raise ValidationError(
            {
                "status": (
                    "Seul un ordre de travail planifié peut être annulé."
                )
            }
        )

# =====================================
# ANNULER UN ORDRE DE TRAVAIL
# =====================================

# cancel_maintenance_work_order
# Annule un ordre de travail encore planifié.
@transaction.atomic
def cancel_maintenance_work_order(
    *,
    work_order: MaintenanceWorkOrder,
    cancellation_reason: str,
    user,
) -> MaintenanceWorkOrder:
    """
    Annule un ordre de travail planifié.

    Le motif d’annulation est obligatoire.
    """

    _ensure_work_order_can_be_cancelled(
        work_order=work_order,
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

    work_order.status = MaintenanceWorkOrderStatus.CANCELLED
    work_order.cancelled_at = timezone.now()
    work_order.cancellation_reason = cancellation_reason
    work_order.updated_by = user

    work_order.save(
        update_fields=[
            "status",
            "cancelled_at",
            "cancellation_reason",
            "updated_by",
            "updated_at",
        ]
    )

    return work_order



# _ensure_work_order_can_be_deleted
# Vérifie qu’un ordre de travail peut être supprimé logiquement.
def _ensure_work_order_can_be_deleted(
    *,
    work_order: MaintenanceWorkOrder,
) -> None:
    """
    Autorise la suppression uniquement pour un ordre planifié.
    """

    if work_order.is_deleted:
        raise ValidationError(
            {
                "work_order": (
                    "Cet ordre de travail est déjà supprimé."
                )
            }
        )

    if work_order.status != MaintenanceWorkOrderStatus.PLANNED:
        raise ValidationError(
            {
                "status": (
                    "Seul un ordre de travail planifié peut être supprimé."
                )
            }
        )

# =====================================
# SUPPRIMER UN ORDRE DE TRAVAIL
# =====================================

# delete_maintenance_work_order
# Supprime logiquement un ordre de travail.
@transaction.atomic
def delete_maintenance_work_order(
    *,
    work_order: MaintenanceWorkOrder,
    user,
    reason: str = "",
) -> MaintenanceWorkOrder:
    """
    Supprime logiquement un ordre de travail.

    Seul un ordre planifié peut être supprimé.

    Args:
        work_order:
            Ordre de travail à supprimer.

        user:
            Utilisateur responsable de la suppression.

        reason:
            Motif facultatif de la suppression.

    Returns:
        MaintenanceWorkOrder:
            L'ordre de travail supprimé logiquement.

    Raises:
        ValidationError:
            Si l'ordre de travail ne peut pas être supprimé.
    """

    _ensure_work_order_can_be_deleted(
        work_order=work_order,
    )

    work_order.is_deleted = True
    work_order.deleted_at = timezone.now()
    work_order.deleted_by = user
    work_order.deleted_reason = reason.strip() or None
    work_order.updated_by = user

    work_order.save(
        update_fields=[
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "deleted_reason",
            "updated_by",
            "updated_at",
        ]
    )

    return work_order