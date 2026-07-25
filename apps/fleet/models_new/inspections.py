
from django.utils import timezone
import uuid

from django.conf import settings
from django.db import models


from apps.fleet.constants import InspectionContext, InspectionCriterionResultValue, InspectionOverallResult, InspectionScoringPolicyStatus, InspectionStatus, VehicleMembershipType

from django.core.exceptions import ValidationError

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Q

from .base import (TimeStampedSoftDeletableModel,)
from .vehicles import Vehicle



# =============================================================================
# InspectionContextVersion
#
# Représente une version complète d’un formulaire d’inspection.
#
# Exemples :
# - DAILY_CHECK 0.0.0
# - DAILY_CHECK 1.0.0
# - DAILY_CHECK 1.1.0
#
# Chaque version possède ses propres sections et ses propres critères.
#
# `source_version` indique la version utilisée comme base lors de la création
# du snapshot.
#
# Exemple :
# - 1.0.0 est créée depuis 0.0.0
# - 1.1.0 est créée depuis 1.0.0
#
# Une ancienne version ne doit pas être modifiée lorsque l’utilisateur
# modifie une nouvelle version.
# =============================================================================
class InspectionVersion(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)

    context = models.CharField(max_length=30,choices=InspectionContext.choices,)

    version = models.CharField(max_length=20,)

    source_version = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="derived_versions",
        null=True,
        blank=True,
    )

    is_current = models.BooleanField(default=False,)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["context", "version"],
                name="unique_inspection_version_per_context",
            ),
        ]

        ordering = [
            "context",
            "-created_at",
        ]

    def __str__(self):
        return f"{self.get_context_display()} - {self.version}"


# InspectionChapter
# Représente un chapitre d’une version d’inspection.
# Exemple : I — Standards minimums.
class InspectionChapter(TimeStampedSoftDeletableModel):
    """
    Représente un chapitre d'une version de formulaire d'inspection.
    Exemple :
        I - Standards minimums
        II - Exigences supplémentaires
    """

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    inspection_version = models.ForeignKey(InspectionVersion,on_delete=models.CASCADE,related_name="chapters",)
    reference = models.CharField(max_length=10,help_text="Référence du chapitre (I, II, III...).",)
    code = models.CharField(max_length=100,help_text="Code technique unique dans une version.",)
    title = models.CharField(max_length=255,help_text="Titre affiché sur la fiche d'inspection.",)
    is_active = models.BooleanField(default=True,help_text="Indique si le chapitre est disponible dans cette version.",)
    position = models.PositiveIntegerField(
    null=True,
    blank=True,
)

    class Meta:
        ordering = [
            "position",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["inspection_version", "reference"],
                name="inspection_chapter_reference_per_version_unique",
            ),
            models.UniqueConstraint(
                fields=["inspection_version", "code"],
                name="inspection_chapter_code_per_version_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.reference} - {self.title}"

# =============================================================================
# InspectionSection
#
# Représente une section appartenant à une version précise du formulaire.
#
# Exemples de références :
# - I
# - II
# - 1
# - 2
#
# Exemple de section :
# - reference = "1"
# - code = "TRACTOR_CONDITION"
# - title = "État du tracteur"
#
# `reference` est la valeur visible dans le formulaire.
#
# `code` est un identifiant technique utilisé par le backend, les imports,
# les tests ou les intégrations.
#
# Une section est propre à une version. Deux versions peuvent donc avoir
# des sections avec le même code, mais ces sections seront deux lignes
# différentes en base de données.
# =============================================================================
class InspectionSection(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)

    chapter = models.ForeignKey(InspectionChapter,on_delete=models.CASCADE,related_name="sections",)
    reference = models.CharField(max_length=20,)
    code = models.CharField(max_length=100,)
    title = models.CharField(max_length=255,)
    is_active = models.BooleanField(default=True,)
    position = models.PositiveIntegerField(
    null=True,
    blank=True,
)

    class Meta:
        constraints = [
        models.UniqueConstraint(
            fields=["chapter", "reference"],
            name="inspection_section_reference_per_chapter_unique",
        ),
        models.UniqueConstraint(
            fields=["chapter", "code"],
            name="inspection_section_code_per_chapter_unique",
        ),
    ]

        ordering = [
            "position",
        ]

    def __str__(self):
        return (
            f"{self.chapter} - "
            f"{self.reference} {self.title}"
        )


# =============================================================================
# InspectionCriterion
#
# Représente un critère appartenant à une section versionnée.
#
# Exemple :
# - reference = "1.1"
# - code = "BRAKES_WORKING"
# - label = "Les freins fonctionnent correctement"
#
# `reference` est le numéro visible dans le formulaire.
#
# `code` est l’identifiant technique du critère.
#
# Le libellé et les règles métier du critère font partie du snapshot.
# Modifier un critère dans une nouvelle version ne modifie donc pas les
# critères des anciennes versions.
#
# La version du critère est accessible par :
#
# criterion.section.inspection_version
# =============================================================================
class InspectionCriterion(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)

    section = models.ForeignKey(InspectionSection,on_delete=models.CASCADE,related_name="criteria",)

    reference = models.CharField(max_length=20,)
    code = models.CharField(max_length=100,)
    label = models.TextField()

    creates_defect_if_failed = models.BooleanField(default=False,)
    is_blocking_if_failed = models.BooleanField(default=False,)
    is_active = models.BooleanField(default=True,)
    position = models.PositiveIntegerField(
    null=True,
    blank=True,
)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["section", "reference"],
                name="unique_criterion_reference_per_section",
            ),
            models.UniqueConstraint(
                fields=["section", "code"],
                name="unique_criterion_code_per_section",
            ),
        ]

        ordering = [
            "position",
        ]

    def __str__(self):
        return f"{self.reference} - {self.label}"


# =============================================================================
# Inspection
#
# Représente une inspection réellement effectuée sur un véhicule.
#
# L’inspection conserve la version exacte du formulaire utilisée.
#
# Exemple :
#
# Une inspection effectuée avec DAILY_CHECK 1.0.0 doit toujours rester
# associée à cette version, même si DAILY_CHECK 2.0.0 devient ensuite
# la version courante.
#
# Le contexte ne doit pas être enregistré une seconde fois directement
# dans Inspection. Il est disponible depuis :
#
# inspection.inspection_version.context
#
# La propriété `context` est fournie comme raccourci.
# =============================================================================
class Inspection(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    vehicle = models.ForeignKey(Vehicle,on_delete=models.PROTECT,related_name="inspections",)

    inspection_version = models.ForeignKey(InspectionVersion,on_delete=models.PROTECT,related_name="inspections",)

    inspection_date = models.DateTimeField()
    inspector = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="inspections",)
    status = models.CharField(max_length=20,choices=InspectionStatus.choices,default=InspectionStatus.IN_PROGRESS,)

    overall_result = models.CharField(max_length=30,choices=InspectionOverallResult.choices,null=True,blank=True,default=None,)
    comments = models.TextField(blank=True,)

    @property
    def context(self):
        return self.inspection_version.context

    def __str__(self):
        return (
            f"{self.vehicle} - "
            f"{self.inspection_version} - "
            f"{self.inspection_date}"
        )


# =============================================================================
# InspectionCriterionResult
#
# Représente le résultat d’un critère pendant une inspection.
#
# Un résultat pointe directement vers un InspectionCriterion versionné.
#
# La contrainte d’unicité empêche d’enregistrer plusieurs résultats pour
# le même critère dans une même inspection.
#
# La méthode `clean()` vérifie que le critère appartient à la même version
# que celle utilisée par l’inspection.
#
# Exemple interdit :
#
# - Inspection créée avec DAILY_CHECK 1.0.0
# - Critère appartenant à DAILY_CHECK 2.0.0
#
# Cette validation devra également être exécutée dans le service métier,
# car Django n’appelle pas automatiquement `clean()` lors d’un `save()`.
# =============================================================================
class InspectionCriterionResult(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)

    inspection = models.ForeignKey(Inspection,on_delete=models.CASCADE,related_name="criterion_results",)

    criterion = models.ForeignKey(InspectionCriterion,on_delete=models.PROTECT,related_name="results",)

    result = models.CharField(max_length=10,choices=InspectionCriterionResultValue.choices,)
    comment = models.TextField(blank=True,)

    class Meta:
        constraints = [
        models.UniqueConstraint(
            fields=["inspection", "criterion"],
            condition=models.Q(is_deleted=False),
            name="unique_active_result_per_inspection_criterion",
        ),
    ]

    def clean(self):
        """
        Validate that the criterion belongs to the inspection version.
        """
        super().clean()

        if not self.inspection_id or not self.criterion_id:
            return

        criterion_version_id = (self.criterion.section.chapter.inspection_version_id)
        inspection_version_id = (self.inspection.inspection_version_id)

        if criterion_version_id != inspection_version_id:
            raise ValidationError(
                {
                    "criterion": (
                        "Le critère n’appartient pas à la version "
                        "utilisée par cette inspection."
                    ),
                }
            )

    def __str__(self):
        return (
            f"{self.inspection} - "
            f"{self.criterion.reference} - "
            f"{self.result}"
        )


# InspectionScoringPolicy
# Defines scoring thresholds by membership type and inspection context.
class InspectionScoringPolicyConfiguration(TimeStampedSoftDeletableModel):
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)
    membership_type = models.CharField(max_length=20,choices=VehicleMembershipType.choices,)
    context = models.CharField(max_length=30,choices=InspectionContext.choices,)
    pass_threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    pass_with_observation_threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )

    status = models.CharField(
        max_length=20,
        choices=InspectionScoringPolicyStatus.choices,
        default=InspectionScoringPolicyStatus.DRAFT,
    )

    activated_at = models.DateTimeField(null=True,blank=True,editable=False,)
    retired_at = models.DateTimeField(null=True,blank=True,editable=False,)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "membership_type",
                    "context",
                ],
                condition=Q(
                    status=InspectionScoringPolicyStatus.ACTIVE,
                    is_deleted=False,
                ),
                name="unique_active_inspection_scoring_policy",
            ),
        ]

    # __str__
    # Returns a readable representation of the scoring policy.
    def __str__(self):
        """
        Return the membership type, context, and status.
        """
        return (
            f"{self.get_membership_type_display()} - "
            f"{self.get_context_display()} - "
            f"{self.get_status_display()}"
        )

