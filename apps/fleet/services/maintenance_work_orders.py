from apps.fleet.models import MaintenanceComponent
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