
import uuid

from django.db import models
from django.conf import settings

from apps.fleet.constants import DowntimeSourceType, DowntimeStatus,ReturnToServiceDecision, ReturnToServiceSourceType


from .base import TimeStampedSoftDeletableModel
from .vehicles import Vehicle

# -------------------------------------------------------------------
# 17-Downtime
# Immobilisation opérationnelle.
# Distincte de Maintenance : toute maintenance peut immobiliser,
# mais toute immobilisation n’est pas forcément une maintenance.
# -------------------------------------------------------------------
class Downtime(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="downtimes")

    # Cause de l’immobilisation.
    source_type = models.CharField(max_length=30, choices=DowntimeSourceType.choices)

    # Référence optionnelle vers la source métier.
    source_id = models.UUIDField(blank=True, null=True)

    # Début de l’immobilisation.
    start_date = models.DateTimeField()

    # Fin de l’immobilisation. Null signifie immobilisation active.
    end_date = models.DateTimeField(blank=True, null=True)

    # Raison de l’immobilisation.
    reason = models.TextField()

    # Statut de l’immobilisation.
    status = models.CharField(max_length=20, choices=DowntimeStatus.choices, default=DowntimeStatus.ACTIVE)

    def __str__(self):
        return f"{self.vehicle} - {self.status}"


# -------------------------------------------------------------------
# 18-ReturnToService
# Décision de remise en service.
# Peut être proposée par le système ou décidée par l’inspecteur.
# -------------------------------------------------------------------
class ReturnToService(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="return_to_services")

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
