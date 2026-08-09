
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


from apps.fleet.constants import (
    VehicleAvailabilityReasonType,
    VehicleAvailabilityResult,
)

from .base import TimeStampedSoftDeletableModel
from .vehicles import Vehicle


# -------------------------------------------------------------------
# 19-VehicleAvailabilityEvaluation
# Évaluation de disponibilité.
# Le système calcule, puis un inspecteur peut valider ou invalider.
# -------------------------------------------------------------------
class VehicleAvailabilityEvaluation(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="availability_evaluations")

    # Date et heure de l’évaluation.
    evaluated_at = models.DateTimeField(
    default=timezone.now,
)

    # Résultat calculé automatiquement.
    calculated_result = models.CharField(max_length=20, choices=VehicleAvailabilityResult.choices)

    # Résultat final après validation/invalidation éventuelle.
    final_result = models.CharField(max_length=20, choices=VehicleAvailabilityResult.choices)

    # Utilisateur ayant validé ou invalidé le calcul.
    validated_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.PROTECT,
    related_name="validated_vehicle_availability_evaluations",
    null=True,
    blank=True,
)

    # Date de validation/invalidation.
    validated_at = models.DateTimeField(blank=True, null=True)

    # Justification si le résultat calculé est modifié.
    validation_comment = models.TextField(blank=True, null=True)

 

    def __str__(self):
        return f"{self.vehicle} - {self.final_result}"


# -------------------------------------------------------------------
# 20-VehicleAvailabilityEvaluationReason
# Raison détaillée d’une évaluation de disponibilité.
# -------------------------------------------------------------------
class VehicleAvailabilityEvaluationReason(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    evaluation = models.ForeignKey(VehicleAvailabilityEvaluation, on_delete=models.CASCADE, related_name="evaluation_reasons")

    # Type de raison normalisée.
    reason_type = models.CharField(max_length=50, choices=VehicleAvailabilityReasonType.choices)

    # Message lisible décrivant la raison.
    message = models.TextField()

    # Identifiant optionnel de l’objet source.
    source_id = models.UUIDField(blank=True, null=True)

    def __str__(self):
        return f"{self.evaluation} - {self.reason_type}"

