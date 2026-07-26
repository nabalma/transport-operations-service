from django.utils import timezone
import uuid

from django.db import models
from apps.fleet.constants import DefectCreationSource, DefectReleaseRequestStatus, DefectStatus, ValidationDecision 
from django.core.exceptions import ValidationError

from .base import (TimeStampedSoftDeletableModel,)
from .vehicles import Vehicle
from .inspections import Inspection, InspectionCriterionResult


# OPEN
#   ↓
# Le réparateur déclare que la correction est terminée
# et soumet une DefectReleaseRequest
#   ↓
# PENDING_VALIDATION
#   ├── validation REJECTED → OPEN
#   └── validation APPROVED → RELEASED
#                               ↓
#                          clôture administrative
#                               ↓
#                             CLOSED



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
# DefectReleaseRequest
# Demande formelle de contrôle après correction d’un défaut.
# Contient la déclaration du réparateur et les références aux preuves.
# -------------------------------------------------------------------
class DefectReleaseRequest(TimeStampedSoftDeletableModel):
    """Représente une demande de levée soumise après correction."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Défaut concerné par la demande de levée.
    defect = models.ForeignKey(
        Defect,
        on_delete=models.PROTECT,
        related_name="release_requests",
    )

    # Résumé des travaux réalisés pour corriger le défaut.
    correction_summary = models.TextField()

    # Personne ou entité ayant soumis la demande.
    submitted_by = models.CharField(
        max_length=255,
    )

    # Date et heure de soumission de la demande.
    submitted_at = models.DateTimeField(
        default=timezone.now,
    )

    # État de traitement de la demande.
    status = models.CharField(
        max_length=20,
        choices=DefectReleaseRequestStatus.choices,
        default=DefectReleaseRequestStatus.PENDING,
    )

    def __str__(self):
        """Retourne une représentation lisible de la demande."""
        return f"{self.defect} - {self.status}"


# -------------------------------------------------------------------
# DefectReleaseValidation
# Décision prise après l’examen d’une demande de levée de défaut.
# Permet d’approuver ou de rejeter officiellement la remise en service.
# -------------------------------------------------------------------
class DefectReleaseValidation(TimeStampedSoftDeletableModel):
    """Représente la validation formelle d’une demande de levée de défaut."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Demande de levée concernée par cette validation.
    release_request = models.OneToOneField(
        DefectReleaseRequest,
        on_delete=models.PROTECT,
        related_name="validation",
    )

    # Décision finale prise par le validateur.
    decision = models.CharField(
        max_length=20,
        choices=ValidationDecision.choices,
    )

    # Personne ou autorité ayant effectué la validation.
    validated_by = models.CharField(
        max_length=255,
    )

    # Date et heure auxquelles la décision a été prise.
    validated_at = models.DateTimeField(
        default=timezone.now,
    )

    # Commentaire expliquant ou justifiant la décision.
    comment = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        """Retourne une représentation lisible de la validation."""
        return f"{self.release_request} - {self.decision}"