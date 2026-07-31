from apps.fleet.constants import MaintenanceWorkOrderStatus
from apps.fleet.models import MaintenanceComponent,MaintenanceWorkOrder,MaintenanceWorkOrderItem
from django.db import transaction
from django.utils import timezone

from django.core.exceptions import ValidationError as DjangoValidationError
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