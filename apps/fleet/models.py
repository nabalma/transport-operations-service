import uuid

from django.conf import settings
from django.db import models

from apps.fleet.upload_paths import vehicle_document_upload_path
from apps.fleet.constants import CarrierStatus, CorrectiveActionStatus, DefectSeverity, DefectSourceType, DefectStatus, DowntimeSourceType, DowntimeStatus, EvidenceOwnerType, EvidenceType,InspectionContext, InspectionCriterionResultValue, InspectionOverallResult, MaintenanceStatus, MaintenanceType, NextTripEligibilityReasonType, NextTripEligibilityResult, ReturnToServiceDecision, ReturnToServiceSourceType, ValidationDecision, VehicleAvailabilityReasonType, VehicleAvailabilityResult, VehicleDocumentType, VehicleMembershipRequestStatus, VehicleMembershipStatus, VehicleMembershipType, VehicleScope, VehicleStatus  

# -------------------------------------------------------------------
# 1-Base model
# Modèle abstrait commun pour created_at et updated_at.
# À hériter par les modèles qui doivent garder ces deux timestamps.
# -------------------------------------------------------------------
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    updated_at = models.DateTimeField(auto_now=True)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

   

    class Meta:
        abstract = True


# -------------------------------------------------------------------
# TimeStampedSoftDeletableModel
# Modèle abstrait ajoutant la suppression logique et sa traçabilité.
# -------------------------------------------------------------------
class TimeStampedSoftDeletableModel(TimeStampedModel):

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    deleted_reason = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

# -------------------------------------------------------------------
# 2-Carrier
# Représente le transporteur. Même s’il n’y en a qu’un seul en V1,
# on le garde comme objet pour l’audit, les rapports et l’évolutivité.
# -------------------------------------------------------------------
class Carrier(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Nom court ou nom commercial du transporteur.
    name = models.CharField(max_length=255)

    address = models.TextField(blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)

    # Permet de désactiver le transporteur sans supprimer l’historique.
    status = models.CharField(max_length=20, choices=CarrierStatus.choices, default=CarrierStatus.ACTIVE)

    def __str__(self):
        return self.name


# -------------------------------------------------------------------
# 3-Vehicle
# Objet principal du module. Représente le camion terrain :
# couple tracteur + citerne. En V1, Tractor et Tanker ne sont pas
# des objets autonomes.
# -------------------------------------------------------------------
class Vehicle(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Transporteur propriétaire/exploitant de la flotte.
    carrier = models.ForeignKey(Carrier, on_delete=models.PROTECT, related_name="vehicles")

    # Immatriculation du tracteur.
    tractor_registration = models.CharField(max_length=50)

    # Année de fabrication du tracteur.
    tractor_manufacture_year = models.PositiveSmallIntegerField(blank=True, null=True)

    # Immatriculation de la citerne.
    tanker_registration = models.CharField(max_length=50)

      # Année de fabrication de la citerne.
    tanker_manufacture_year = models.PositiveSmallIntegerField(blank=True, null=True)


    # Immatriculation affichée : tracteur / citerne. Calculée dans save().
    display_registration = models.CharField(max_length=120, editable=False)

    # Date de début de l’attelage tracteur + citerne.
    vehicle_coupling_start_date = models.DateField()

    # Date de fin de cet attelage. Null signifie attelage actif.
    vehicle_coupling_end_date = models.DateField(blank=True, null=True)

    # Statut général. Ne remplace pas l’éligibilité ni la disponibilité.
    status = models.CharField(max_length=30, choices=VehicleStatus.choices, default=VehicleStatus.ACTIVE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["tractor_registration", "tanker_registration", "vehicle_coupling_end_date"], name="unique_vehicle_coupling_period")
        ]

    def save(self, *args, **kwargs):
        self.display_registration = f"{self.tractor_registration} / {self.tanker_registration}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_registration


# -------------------------------------------------------------------
# 4-TankerCompartment
# Représente un compartiment de la citerne du Vehicle.
# -------------------------------------------------------------------
class TankerCompartment(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="tanker_compartments")

    # Numéro du compartiment dans la citerne : 1, 2, 3...
    compartment_number = models.PositiveSmallIntegerField()

    # Capacité du compartiment, par exemple en litres.
    capacity_liters = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["vehicle", "compartment_number"], name="unique_compartment_number_per_vehicle")
        ]

    def __str__(self):
        return f"{self.vehicle} - Compartiment {self.compartment_number}"




# -------------------------------------------------------------------
# 5-vehicleMembership
# Historique d’appartenance du Vehicle à la flotte.
# Ne pas remplacer par un simple booléen is_in_fleet.
# -------------------------------------------------------------------
class VehicleMembership(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Vehicle concerné.
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="vehicle_memberships")

    # Transporteur concerné. Utile pour audit, même avec un seul transporteur.
    carrier = models.ForeignKey(Carrier, on_delete=models.PROTECT, related_name="vehicle_memberships")

    # Date d’entrée dans la flotte.
    entry_date = models.DateField()

    # Date de sortie de flotte. Null signifie appartenance active.
    exit_date = models.DateField(blank=True, null=True)

    # Type d’appartenance : spot ou contractuelle.
    membership_type = models.CharField(max_length=20, choices=VehicleMembershipType.choices, default=VehicleMembershipType.SPOT)

    # Statut de la période d’appartenance.
    status = models.CharField(max_length=20, choices=VehicleMembershipStatus.choices, default=VehicleMembershipStatus.ACTIVE)

    def __str__(self):
        return f"{self.vehicle} - {self.status}"



# -------------------------------------------------------------------
# 5-VehicleMembershipRequest
# Demande d’ajout d’un véhicule à la flotte.
# Le superviseur prépare et soumet la demande.
# Le manager peut ensuite l’approuver ou la rejeter.
# Une approbation entraîne la création d’un vehicleMembership.
# -------------------------------------------------------------------
class VehicleMembershipRequest(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False,)

    # Véhicule concerné par la demande.
    vehicle = models.ForeignKey(Vehicle,on_delete=models.PROTECT,related_name="membership_requests",)

    # Transporteur auquel le véhicule doit être rattaché.
    carrier = models.ForeignKey(Carrier,on_delete=models.PROTECT,related_name="vehicle_membership_requests",)

    # Date d’entrée souhaitée dans la flotte.
    requested_entry_date = models.DateField()

    # Type d’appartenance demandé : spot ou contractuelle.
    membership_type = models.CharField(max_length=20,choices=VehicleMembershipType.choices,default=VehicleMembershipType.SPOT,)

    # État courant du workflow d’approbation.
    status = models.CharField(max_length=20,choices=VehicleMembershipRequestStatus.choices,default=VehicleMembershipRequestStatus.DRAFT,)

    # Manager ayant approuvé ou rejeté la demande.
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,blank=True,null=True,related_name="decided_vehicle_membership_requests",)

    # Date et heure de la décision du manager.
    decided_at = models.DateTimeField(blank=True,null=True,)

    # Commentaire fourni lors de l’approbation ou du rejet.
    decision_comment = models.TextField(blank=True,null=True,)

    def __str__(self):
        return f"{self.vehicle} - {self.status}"






# -------------------------------------------------------------------
# 6-VehicleDocument
# Document lié au Vehicle, au tracteur ou à la citerne.
# La validité est calculée via expires_at.
# -------------------------------------------------------------------
class VehicleDocument(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="documents")

    # Scope du document : véhicule complet, tracteur ou citerne.
    scope = models.CharField(max_length=20, choices=VehicleScope.choices)

    # Type de document : assurance, certificat citerne, carte grise, etc.
    document_type = models.CharField(max_length=100, choices=VehicleDocumentType.choices)

    # Numéro officiel ou référence du document.
    reference_number = models.CharField(max_length=100, blank=True, null=True)

    # Date d’émission du document.
    issued_date = models.DateField(blank=True, null=True)

    # Date d’expiration. Utilisée pour l’éligibilité et le Trip Readiness.
    expires_at = models.DateField(blank=True, null=True)

    # Nom original du fichier uploadé par l’utilisateur.
    # Stocké pour affichage, audit et traçabilité.
    # Le vrai nom physique du fichier est géré par le champ file.
    original_filename = models.CharField(max_length=255, blank=True, null=True)

    # Lien vers le fichier justificatif. Peut évoluer vers Evidence.
    file = models.FileField(upload_to=vehicle_document_upload_path, max_length=500,blank=True,null=True)

    def __str__(self):
        return f"{self.vehicle} - {self.document_type}"


# -------------------------------------------------------------------
# 7-InspectionSection
# Section réutilisable d’un questionnaire d’inspection.
# Exemple : ÉTAT DU TRACTEUR, ÉTAT DE LA CITERNE.
# -------------------------------------------------------------------
class InspectionSection(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Code stable de la section.
    code = models.CharField(max_length=100, unique=True)

    # Titre affiché dans la fiche d’inspection.
    title = models.CharField(max_length=255)

    # Permet de désactiver une section sans supprimer l’historique.
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


# -------------------------------------------------------------------
# 8-InspectionCriterion
# Critère stable d’inspection.
# Exemple : ceinture fonctionnelle, fuite citerne, klaxon fonctionnel.
# -------------------------------------------------------------------
class InspectionCriterion(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Code stable du critère.
    code = models.CharField(max_length=100, unique=True)

    # Question ou libellé affiché à l’inspecteur.
    label = models.TextField()

    # Partie concernée : VEHICLE, TRACTOR ou TANKER.
    scope = models.CharField(max_length=20, choices=VehicleScope.choices)

    # Si true, un FAIL crée automatiquement un Defect.
    creates_defect_if_failed = models.BooleanField(default=False)

    # Si true, le Defect créé sera bloquant.
    is_blocking_if_failed = models.BooleanField(default=False)

    # Permet de désactiver un critère sans supprimer l’historique.
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


# -------------------------------------------------------------------
# 9-InspectionContextSection
# Place une section dans un contexte d’inspection.
# Exemple : section ÉTAT DU TRACTEUR en position "1" dans BEFORE_TRIP.
# -------------------------------------------------------------------
class InspectionContextSection(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Contexte d’inspection : périodique, avant voyage, après incident, etc.
    context = models.CharField(max_length=30, choices=InspectionContext.choices)

    # Section réutilisable placée dans ce contexte.
    section = models.ForeignKey(InspectionSection, on_delete=models.PROTECT, related_name="context_sections")

    # Référence affichée dans la fiche : "1", "2", "3", etc.
    reference = models.CharField(max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["context", "section"], name="unique_section_per_inspection_context"),
            models.UniqueConstraint(fields=["context", "reference"], name="unique_section_reference_per_context"),
        ]

    def __str__(self):
        return f"{self.context} - {self.reference} {self.section.title}"


# -------------------------------------------------------------------
# 10-InspectionContextCriterion
# Place un critère dans une section utilisée par un contexte donné.
# Exemple : 1.1 - Ceinture de sécurité.
# -------------------------------------------------------------------
class InspectionContextCriterion(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Section de contexte dans laquelle le critère apparaît.
    context_section = models.ForeignKey(InspectionContextSection, on_delete=models.CASCADE, related_name="context_criteria")

    # Critère stable réutilisable.
    criterion = models.ForeignKey(InspectionCriterion, on_delete=models.PROTECT, related_name="context_criteria")

    # Référence affichée dans la fiche : "1.1", "2.2", etc.
    reference = models.CharField(max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["context_section", "criterion"], name="unique_criterion_per_context_section"),
            models.UniqueConstraint(fields=["context_section", "reference"], name="unique_criterion_reference_per_context_section"),
        ]

    def __str__(self):
        return f"{self.reference} - {self.criterion.code}"


# -------------------------------------------------------------------
# 11-Inspection
# Inspection réelle effectuée sur un Vehicle.
# Les lignes de contrôle sont dans InspectionCriterionResult.
# -------------------------------------------------------------------
class Inspection(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="inspections")

    # Contexte de l’inspection.
    context = models.CharField(max_length=30, choices=InspectionContext.choices)

    # Date et heure réelles de l’inspection.
    inspection_date = models.DateTimeField()

    # Nom de l’inspecteur. Peut devenir inspector_id plus tard.
    inspector_name = models.CharField(max_length=255)

    # Résultat global de toute l’inspection.
    overall_result = models.CharField(max_length=30, choices=InspectionOverallResult.choices)

    # Commentaire général de l’inspection.
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"{self.vehicle} - {self.context} - {self.inspection_date}"


# -------------------------------------------------------------------
# 12-InspectionCriterionResult
# Résultat d’un critère précis pendant une inspection réelle.
# Peut générer automatiquement un Defect selon le critère.
# -------------------------------------------------------------------
class InspectionCriterionResult(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name="criterion_results")

    # Critère placé dans la fiche utilisée par cette inspection.
    context_criterion = models.ForeignKey(InspectionContextCriterion, on_delete=models.PROTECT, related_name="inspection_results")

    # Résultat du contrôle : PASS ou FAIL.
    result = models.CharField(max_length=10, choices=InspectionCriterionResultValue.choices)

    # Commentaire spécifique au critère.
    comment = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["inspection", "context_criterion"], name="unique_result_per_inspection_criterion")
        ]

    def __str__(self):
        return f"{self.inspection} - {self.context_criterion.reference} - {self.result}"


# -------------------------------------------------------------------
# 13-Defect
# Défaut/anomalie nécessitant un suivi.
# Peut être créé depuis une inspection, une observation, un incident ou une maintenance.
# -------------------------------------------------------------------
class Defect(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="defects")

    # Origine du défaut.
    source_type = models.CharField(max_length=30, choices=DefectSourceType.choices)

    # Inspection source si le défaut vient d’une inspection.
    source_inspection = models.ForeignKey(Inspection, on_delete=models.SET_NULL, blank=True, null=True, related_name="defects")

    # Résultat précis ayant généré le défaut.
    source_inspection_criterion_result = models.OneToOneField(InspectionCriterionResult, on_delete=models.SET_NULL, blank=True, null=True, related_name="defect")

    # Partie concernée par le défaut.
    scope = models.CharField(max_length=20, choices=VehicleScope.choices)

    # Description du défaut constaté.
    description = models.TextField()

    # Gravité métier ou technique.
    severity = models.CharField(max_length=20, choices=DefectSeverity.choices)

    # Si true, rend le Vehicle non éligible tant que le blocage n’est pas levé.
    is_blocking = models.BooleanField(default=False)

    # Cycle de vie du défaut.
    status = models.CharField(max_length=30, choices=DefectStatus.choices, default=DefectStatus.OPEN)

    # Date de détection du défaut.
    detected_at = models.DateTimeField()

    def __str__(self):
        return f"{self.vehicle} - {self.severity} - {self.status}"


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


# -------------------------------------------------------------------
# 16-Maintenance
# Maintenance préventive ou corrective.
# Le blocage métier est porté par Defect, pas par Maintenance.
# -------------------------------------------------------------------
class Maintenance(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="maintenances")

    # Partie concernée par la maintenance.
    scope = models.CharField(max_length=20, choices=VehicleScope.choices)

    # Type de maintenance : préventive ou corrective.
    type = models.CharField(max_length=20, choices=MaintenanceType.choices)

    # Statut de la maintenance.
    status = models.CharField(max_length=20, choices=MaintenanceStatus.choices, default=MaintenanceStatus.PLANNED)

    planned_start_date = models.DateTimeField(blank=True, null=True)
    planned_end_date = models.DateTimeField(blank=True, null=True)
    actual_start_date = models.DateTimeField(blank=True, null=True)
    actual_end_date = models.DateTimeField(blank=True, null=True)

    # Description libre de l’intervention.
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.vehicle} - {self.type} - {self.status}"


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
    decided_by = models.CharField(max_length=255, blank=True, null=True)

    # Date de décision.
    decided_at = models.DateTimeField(blank=True, null=True)

    # Commentaire de décision.
    comment = models.TextField(blank=True, null=True)

    # Preuve de remise en service. Peut évoluer vers Evidence.
    evidence_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.vehicle} - {self.decision}"


# -------------------------------------------------------------------
# 19-VehicleAvailabilityEvaluation
# Évaluation de disponibilité.
# Le système calcule, puis un inspecteur peut valider ou invalider.
# -------------------------------------------------------------------
class VehicleAvailabilityEvaluation(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="availability_evaluations")

    # Date et heure de l’évaluation.
    evaluated_at = models.DateTimeField()

    # Résultat calculé automatiquement.
    calculated_result = models.CharField(max_length=20, choices=VehicleAvailabilityResult.choices)

    # Résultat final après validation/invalidation éventuelle.
    final_result = models.CharField(max_length=20, choices=VehicleAvailabilityResult.choices)

    # Version des règles utilisées.
    rule_version = models.CharField(max_length=50)

    # Utilisateur ayant validé ou invalidé le calcul.
    validated_by = models.CharField(max_length=255, blank=True, null=True)

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


# -------------------------------------------------------------------
# 21-NextTripEligibilityEvaluation
# Évaluation d’éligibilité pour le prochain voyage.
# Toutes les évaluations sont conservées pour audit.
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# 23-Evidence
# Preuve transverse.
# Peut être liée à une inspection, un défaut, une correction,
# une maintenance, une remise en service ou une évaluation.
# -------------------------------------------------------------------
class Evidence(TimeStampedSoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Type d’objet auquel la preuve est rattachée.
    owner_type = models.CharField(max_length=50, choices=EvidenceOwnerType.choices)

    # Identifiant de l’objet propriétaire.
    owner_id = models.UUIDField()

    # Type de preuve.
    evidence_type = models.CharField(max_length=30, choices=EvidenceType.choices)

    # Fichier ou photo si applicable.
    file_url = models.URLField(blank=True, null=True)

    # Description de la preuve.
    description = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"{self.owner_type} - {self.evidence_type}"
    
