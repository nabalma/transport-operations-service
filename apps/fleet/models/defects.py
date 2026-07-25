from django.utils import timezone
import uuid

from django.db import models

from apps.fleet.constants import CorrectiveActionStatus, DefectCreationSource, DefectStatus, ValidationDecision 

from django.core.exceptions import ValidationError

from .base import (TimeStampedSoftDeletableModel,)
from .vehicles import Vehicle
from .inspections import Inspection, InspectionCriterionResult

# -------------------------------------------------------------------
# 13-Defect
# Défaut/anomalie nécessitant un suivi.
# Peut être créé depuis une inspection, une observation, un incident ou une maintenance.
# -------------------------------------------------------------------
class Defect(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="defects")

    # Origine du défaut.
    creation_source = models.CharField(max_length=20,choices=DefectCreationSource.choices,default=DefectCreationSource.USER,)

    # Inspection source si le défaut vient d’une inspection.
    source_inspection = models.ForeignKey(Inspection, on_delete=models.SET_NULL, blank=True, null=True, related_name="defects")

    # Résultat précis ayant généré le défaut.
    source_inspection_criterion_result = models.OneToOneField(InspectionCriterionResult, on_delete=models.SET_NULL, blank=True, null=True, related_name="defect")

    # Description du défaut constaté.
    description = models.TextField()

   # Cycle de vie du défaut.
    status = models.CharField(max_length=30, choices=DefectStatus.choices, default=DefectStatus.OPEN)

    # Date de détection du défaut.
    detected_at = models.DateTimeField(default=timezone.now,)

    def __str__(self):
        return f"{self.vehicle} - {self.status}"

    # clean
    # Valide la cohérence des informations sources du défaut.
    def clean(self):
        """
        Validate that the criterion result belongs to the source inspection.
        """
        super().clean()

        if (
            self.source_inspection_criterion_result
            and self.source_inspection
            and self.source_inspection_criterion_result.inspection_id
            != self.source_inspection_id
        ):
            raise ValidationError(
                {
                    "source_inspection_criterion_result": (
                        "The criterion result does not belong to "
                        "the source inspection."
                    )
                }
            )


# -------------------------------------------------------------------
# 14-CorrectiveAction
# Action corrective associée à un Defect.
# Une correction ne clôture pas automatiquement un défaut bloquant.
# -------------------------------------------------------------------
class CorrectiveAction(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    defect = models.ForeignKey(Defect, on_delete=models.CASCADE, related_name="corrective_actions")

    # Description de l’action réalisée.
    description = models.TextField()

    # Personne ou entité ayant réalisé la correction.
    performed_by = models.CharField(max_length=255)

    # Date de réalisation de l’action corrective.
    performed_at = models.DateTimeField()

    # État de l’action corrective.
    status = models.CharField(max_length=20, choices=CorrectiveActionStatus.choices, default=CorrectiveActionStatus.PLANNED)

    # Preuve de correction. Peut évoluer vers Evidence.
    evidence_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.defect} - {self.status}"


# -------------------------------------------------------------------
# 15-DefectReleaseValidation
# Validation de levée d’un défaut bloquant.
# Distincte de la correction.
# -------------------------------------------------------------------
class DefectReleaseValidation(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    defect = models.ForeignKey(Defect, on_delete=models.CASCADE, related_name="release_validations")

    # Décision de validation : APPROVED ou REJECTED.
    decision = models.CharField(max_length=20, choices=ValidationDecision.choices)

    # Inspecteur ou autorité ayant validé.
    validated_by = models.CharField(max_length=255)

    # Date et heure de validation.
    validated_at = models.DateTimeField()

    # Commentaire de validation.
    comment = models.TextField(blank=True, null=True)

    # Preuve de validation. Peut évoluer vers Evidence.
    validation_evidence_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.defect} - {self.decision}"

