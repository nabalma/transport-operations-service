import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


# -------------------------------------------------------------------
# 21-NextTripEligibilityEvaluation
# Évaluation d’éligibilité pour le prochain voyage.
# Toutes les évaluations sont conservées pour audit.
# -------------------------------------------------------------------
from apps.fleet.models.vehicles import Vehicle
from apps.trips.constants import NextTripEligibilityReasonType, NextTripEligibilityResult
from apps.trips.models.base import TimeStampedSoftDeletableModel


class NextTripEligibilityEvaluation(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="eligibility_evaluations")

    # Date et heure de l’évaluation.
    evaluated_at = models.DateTimeField()

    # Résultat d’éligibilité.
    result = models.CharField(max_length=20, choices=NextTripEligibilityResult.choices)

    # Version des règles d’éligibilité.
    rule_version = models.CharField(max_length=50)

    # Snapshot des faits utilisés pour calculer le résultat.
    source_facts = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.vehicle} - {self.result}"


# -------------------------------------------------------------------
# 22-NextTripEligibilityEvaluationReason
# Raison détaillée d’une évaluation d’éligibilité.
# -------------------------------------------------------------------
class NextTripEligibilityEvaluationReason(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    evaluation = models.ForeignKey(NextTripEligibilityEvaluation, on_delete=models.CASCADE, related_name="evaluation_reasons")

    # Type de raison normalisée.
    reason_type = models.CharField(max_length=50, choices=NextTripEligibilityReasonType.choices)

    # Message lisible décrivant la raison.
    message = models.TextField()

    # Identifiant optionnel de l’objet source.
    source_id = models.UUIDField(blank=True, null=True)

    def __str__(self):
        return f"{self.evaluation} - {self.reason_type}"
