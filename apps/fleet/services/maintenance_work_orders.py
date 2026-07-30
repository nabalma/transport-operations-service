from apps.fleet.constants import MaintenanceWorkOrderStatus
from apps.fleet.models import MaintenanceComponent,MaintenanceWorkOrder,MaintenanceWorkOrderItem
from django.db import transaction

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
def _ensure_work_order_accepts_items(
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

    _ensure_work_order_accepts_items(
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