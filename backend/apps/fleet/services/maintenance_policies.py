from django.db import transaction

from apps.fleet.models import MaintenancePolicy


@transaction.atomic
def create_maintenance_policy(
    *,
    user,
    code: str,
    name: str,
    description: str = "",
    interval_days: int | None = None,
    interval_mileage: int | None = None,
    interval_engine_hours: int | None = None,
    tolerance_days: int = 0,
    tolerance_mileage: int = 0,
    tolerance_engine_hours: int = 0,
    is_active: bool = True,
) -> MaintenancePolicy:
    """
    Crée une politique de maintenance préventive.
    Au moins un intervalle doit être défini.
    """
    policy = MaintenancePolicy(
        code=code.strip().upper(),
        name=name.strip(),
        description=description.strip(),
        interval_days=interval_days,
        interval_mileage=interval_mileage,
        interval_engine_hours=interval_engine_hours,
        tolerance_days=tolerance_days,
        tolerance_mileage=tolerance_mileage,
        tolerance_engine_hours=tolerance_engine_hours,
        is_active= is_active,
        created_by=user,
        updated_by=user,
    )

    policy.full_clean()
    policy.save()

    return policy