
import uuid

from django.db import models
from django.conf import settings

from apps.fleet.constants import DowntimeStatus,ReturnToServiceDecision, ReturnToServiceSourceType


from .base import TimeStampedSoftDeletableModel
from .vehicles import Vehicle


# -------------------------------------------------------------------
# Downtime
# Représente une période globale d’immobilisation d’un véhicule.
# Les raisons de l’immobilisation sont enregistrées dans DowntimeCause.
# -------------------------------------------------------------------
class Downtime(TimeStampedSoftDeletableModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name="downtimes",
    )

    # Début de l’immobilisation.
    start_date = models.DateTimeField()

    # Fin de l’immobilisation.
    # Une valeur nulle signifie que l’immobilisation est toujours active.
    end_date = models.DateTimeField(
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=DowntimeStatus.choices,
        default=DowntimeStatus.ACTIVE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("vehicle",),
                condition=models.Q(
                    status=DowntimeStatus.ACTIVE,
                    end_date__isnull=True,
                    is_deleted=False,
                ),
                name="unique_active_downtime_per_vehicle",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.vehicle} - {self.status}"


# -------------------------------------------------------------------
# DowntimeCause
# Représente une cause individuelle liée à une immobilisation.
#
# Une immobilisation peut avoir plusieurs causes :
# - défaut issu d’un critère bloquant en échec ;
# - décision manuelle ;
# - autre cause ajoutée ultérieurement.
# -------------------------------------------------------------------
class DowntimeCause(TimeStampedSoftDeletableModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    downtime = models.ForeignKey(
        Downtime,
        on_delete=models.PROTECT,
        related_name="causes",
    )

    inspection_criterion_result = models.ForeignKey(
    "fleet.InspectionCriterionResult",
    on_delete=models.PROTECT,
    related_name="downtime_causes",
    null=True,
    blank=True,
    )

   # Défaut éventuellement créé à partir du même échec d’inspection.
# Il reste facultatif, car un critère bloquant peut ne pas créer de défaut.
    defect = models.ForeignKey(
        "fleet.Defect",
        on_delete=models.PROTECT,
        related_name="downtime_causes",
        blank=True,
        null=True,
    )

    # Principalement utilisé pour les causes manuelles.
    # Peut également apporter un complément d’information à un défaut.
    reason = models.TextField(
        blank=True,
        default="",
    )

    # Indique si cette cause particulière a été résolue.
    is_resolved = models.BooleanField(
        default=False,
    )

    resolved_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="resolved_downtime_causes",
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        if self.inspection_criterion_result_id:
            return (
                f"{self.downtime_id} - Résultat d’inspection "
                f"{self.inspection_criterion_result_id}"
            )

        if self.defect_id:
            return f"{self.downtime_id} - Défaut {self.defect_id}"

        return f"{self.downtime_id} - {self.reason}"

# -------------------------------------------------------------------
# 18-ReturnToService
# Décision de remise en service.
# Peut être proposée par le système ou décidée par l’inspecteur.
# -------------------------------------------------------------------
class ReturnToService(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="return_to_services")

    downtime = models.ForeignKey(
    "fleet.Downtime",
    on_delete=models.PROTECT,
    related_name="return_to_services",
    null=True,
    blank=True,
    )

    # Origine de la remise en service.
    source_type = models.CharField(max_length=30, choices=ReturnToServiceSourceType.choices)

    # Référence à l’objet source si applicable.
    source_id = models.UUIDField(blank=True, null=True)

    # True si le système a proposé la remise en service.
    proposed_by_system = models.BooleanField(default=False)

    # Décision : PENDING, APPROVED ou REJECTED.
    decision = models.CharField(max_length=20, choices=ReturnToServiceDecision.choices, default=ReturnToServiceDecision.PENDING)

    # Inspecteur ou autorité ayant décidé.
    decided_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.PROTECT,
    related_name="return_to_service_decisions",
    null=True,
    blank=True,
)

    # Date de décision.
    decided_at = models.DateTimeField(blank=True, null=True)

    # Commentaire de décision.
    comment = models.TextField(blank=True, null=True)

    # Preuve de remise en service. Peut évoluer vers Evidence.
    evidence_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.vehicle} - {self.decision}"
