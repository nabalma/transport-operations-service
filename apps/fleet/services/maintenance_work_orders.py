from apps.fleet.constants import MaintenanceWorkOrderKind, MaintenanceWorkOrderStatus
from apps.fleet.models import Vehicle,MaintenanceSchedule,Defect,MaintenanceComponent,MaintenanceWorkOrder,MaintenanceWorkOrderItem
from django.db import transaction
from django.utils import timezone

from django.core.exceptions import ValidationError as DjangoValidationError
from datetime import datetime
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

    _ensure_work_order_origin_matches_kind(
        kind=kind,
        schedule=schedule,
        defect=defect,
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