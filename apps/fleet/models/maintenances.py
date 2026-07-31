# models/maintenance.py

import uuid

from django.db import models
from django.db.models import Q

from apps.fleet.constants import MaintenanceScheduleStatus, MaintenanceWorkOrderKind, MaintenanceWorkOrderStatus, VehicleScope

from .base import TimeStampedSoftDeletableModel



# Définit les règles configurables d’un programme de maintenance préventive.
# Elle précise les intervalles et les tolérances applicables.
# Elle ne représente ni une échéance concrète ni une intervention réalisée.
class MaintenancePolicy(TimeStampedSoftDeletableModel):
    """
    Configuration d’une politique de maintenance préventive.
    Elle centralise les fréquences et les tolérances métier.
    """
    id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False,
    )
    code = models.CharField(max_length=50,unique=True,)
    name = models.CharField(max_length=255,)
    description = models.TextField(blank=True,)

    interval_days = models.PositiveIntegerField(null=True,blank=True,)
    interval_mileage = models.PositiveBigIntegerField(null=True,blank=True,)
    interval_engine_hours = models.PositiveBigIntegerField(null=True,blank=True,)

    tolerance_days = models.PositiveIntegerField(default=0,)
    tolerance_mileage = models.PositiveBigIntegerField(default=0,)
    tolerance_engine_hours = models.PositiveBigIntegerField(default=0,)

    is_active = models.BooleanField(default=True,)

    class Meta:
        ordering = ("name",)
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(interval_days__isnull=False)
                    | Q(interval_mileage__isnull=False)
                    | Q(interval_engine_hours__isnull=False)
                ),
                name="maintenance_policy_requires_interval",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


# Représente une échéance préventive pour un véhicule.
# Elle dépend d’une politique de maintenance configurée.
# Une seule planification active est autorisée par véhicule et politique.
class MaintenanceSchedule(TimeStampedSoftDeletableModel):

    """
    Échéance préventive d’un véhicule selon une politique donnée.
    Une seule planification active est autorisée par véhicule et politique.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        )
        
    vehicle = models.ForeignKey(
        "fleet.Vehicle",
        on_delete=models.PROTECT,
        related_name="maintenance_schedules",
    )

    policy = models.ForeignKey(
        "fleet.MaintenancePolicy",
        on_delete=models.PROTECT,
        related_name="maintenance_schedules",
    )

    status = models.CharField(
        max_length=20,
        choices=MaintenanceScheduleStatus.choices,
        default=MaintenanceScheduleStatus.ACTIVE,
    )

    due_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    due_mileage = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )

    due_engine_hours = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )

    fulfilled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    cancellation_reason = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = (
            "due_at",
            "due_mileage",
            "due_engine_hours",
        )

        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(due_at__isnull=False)
                    | models.Q(due_mileage__isnull=False)
                    | models.Q(due_engine_hours__isnull=False)
                ),
                name="maintenance_schedule_requires_due",
            ),
                models.UniqueConstraint(
                fields=("vehicle", "policy"),
                condition=models.Q(
                    status=MaintenanceScheduleStatus.ACTIVE,
                    is_deleted=False,
                ),
                name="unique_active_schedule_per_vehicle_policy",
            )
        ]

    def __str__(self):
      return (
    f"{self.vehicle} - "
    f"{self.policy.name} "
    f"({self.status})"
)





# -------------------------------------------------------------------
# MaintenanceComponent
# Catalogue des composants pouvant faire l'objet d'une maintenance.
# Les composants sont rattachés à un scope véhicule.
# -------------------------------------------------------------------
#
# Représente un composant standard du véhicule pouvant être utilisé
# dans un ordre de travail.
#
class MaintenanceComponent(TimeStampedSoftDeletableModel):
    """
    Catalogue des composants de maintenance.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    code = models.CharField(
        max_length=50,
        unique=True,
    )

    name = models.CharField(
        max_length=150,
    )

    scope = models.CharField(
        max_length=20,
        choices=VehicleScope.choices,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "scope",
            "name",
        ]

    def __str__(self):
        return f"{self.scope} - {self.name}"




# -------------------------------------------------------------------
# MaintenanceWorkOrderItem
#
# Représente une intervention précise à l’intérieur d’un ordre de travail.
#
# Un ordre de travail peut contenir plusieurs éléments.
# Chaque élément concerne un composant de maintenance précis.
#
# Exemple :
# - pneus ;
# - freins ;
# - moteur ;
# - trou d’homme ;
# - vanne.
#
# Le scope n’est pas stocké directement sur ce modèle.
# Il est déterminé à partir du composant associé afin d’éviter
# les incohérences entre le composant et sa partie du véhicule.
# -------------------------------------------------------------------
class MaintenanceWorkOrderItem(TimeStampedSoftDeletableModel):
    """
    Représente une intervention précise dans un ordre de travail.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    work_order = models.ForeignKey(
        "fleet.MaintenanceWorkOrder",
        on_delete=models.PROTECT,
        related_name="items",
    )

    component = models.ForeignKey(
        "fleet.MaintenanceComponent",
        on_delete=models.PROTECT,
        related_name="work_order_items",
    )

    description = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = [
            "created_at",
        ]

    def __str__(self):
        return f"{self.work_order} - {self.component}"





# -------------------------------------------------------------------
# MaintenanceWorkOrder
#
# Représente un ordre de travail de maintenance.
#
# Un ordre de travail regroupe une ou plusieurs interventions
# MaintenanceWorkOrderItem exécutées sur un même véhicule.
#
# Il peut être :
# - préventif, lorsqu’il provient d’une MaintenanceSchedule ;
# - correctif, lorsqu’il est créé à la suite d’un défaut ou d’un besoin
#   de réparation.
#
# Règles métier :
#
# PREVENTIVE
# - schedule obligatoire ;
# - defect interdit.
#
# CORRECTIVE
# - schedule interdit ;
# - defect facultatif.
#
# Son cycle de vie est indépendant des immobilisations
# et des décisions de remise en service.
# -------------------------------------------------------------------
class MaintenanceWorkOrder(TimeStampedSoftDeletableModel):
    """
    Représente un ordre de travail de maintenance.

    Les interventions précises sont enregistrées dans les
    MaintenanceWorkOrderItem associés.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    vehicle = models.ForeignKey(
        "fleet.Vehicle",
        on_delete=models.PROTECT,
        related_name="maintenance_work_orders",
    )

    kind = models.CharField(
        max_length=20,
        choices=MaintenanceWorkOrderKind.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=MaintenanceWorkOrderStatus.choices,
        default=MaintenanceWorkOrderStatus.PLANNED,
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    schedule = models.ForeignKey(
        "fleet.MaintenanceSchedule",
        on_delete=models.PROTECT,
        related_name="work_orders",
        null=True,
        blank=True,
    )

    defect = models.ForeignKey(
        "fleet.Defect",
        on_delete=models.PROTECT,
        related_name="maintenance_work_orders",
        null=True,
        blank=True,
    )

    planned_start_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    planned_end_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completion_notes = models.TextField(
        blank=True,
    )

    cancellation_reason = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = (
            "-created_at",
        )

        constraints = [
            models.CheckConstraint(
                condition=(
                    (
                        Q(
                            kind=MaintenanceWorkOrderKind.PREVENTIVE,
                            schedule__isnull=False,
                            defect__isnull=True,
                        )
                    )
                    |
                    (
                        Q(
                            kind=MaintenanceWorkOrderKind.CORRECTIVE,
                            schedule__isnull=True,
                        )
                    )
                ),
                name="maintenance_work_order_origin_matches_kind",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} - {self.vehicle}"

