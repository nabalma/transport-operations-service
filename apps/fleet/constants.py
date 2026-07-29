from django.db import models


# ---------------------------------------------
# MODELS
# ---------------------------------------------


# -------------------------------------------------------------------
# CarrierStatus
# Statut du transporteur.
# -------------------------------------------------------------------
class CarrierStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"


# -------------------------------------------------------------------
# VehicleStatus
# Statut général du véhicule.
# Ne remplace pas Availability ni Eligibility.
# -------------------------------------------------------------------
class VehicleStatus(models.TextChoices):
    AWAITING_FLEET_ENTRY = "AWAITING_FLEET_ENTRY", "Awaiting fleet entry"
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"
    OUT_OF_SERVICE = "OUT_OF_SERVICE", "Out of service"


# -------------------------------------------------------------------
# FleetMembershipStatus
# Statut d’une période d’appartenance à la flotte.
# -------------------------------------------------------------------
class VehicleMembershipStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    ENDED = "ENDED", "Ended"


# -------------------------------------------------------------------
# FleetMembershipType
# Type d’appartenance du véhicule à la flotte.
# -------------------------------------------------------------------
class VehicleMembershipType(models.TextChoices):
    SPOT = "SPOT", "Spot"
    CONTRACTUAL = "CONTRACTUAL", "Contractual"

# -------------------------------------------------------------------
# VehicleMembershipRequestStatus
# Statut du workflow d’une demande d’appartenance à la flotte.
# Permet de suivre la demande depuis sa préparation jusqu’à sa décision
# finale ou son annulation.
# -------------------------------------------------------------------
class VehicleMembershipRequestStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    CANCELLED = "CANCELLED", "Cancelled"

# -------------------------------------------------------------------
# VehicleScope
# Scope métier concerné par un document, critère, défaut ou maintenance.
# VEHICLE = le camion/attelage complet.
# TRACTOR = uniquement le tracteur.
# TANKER = uniquement la citerne.
# -------------------------------------------------------------------
class VehicleScope(models.TextChoices):
    VEHICLE = "VEHICLE", "Vehicle"
    TRACTOR = "TRACTOR", "Tractor"
    TANKER = "TANKER", "Tanker"

# -------------------------------------------------------------------
# VehicleAgePolicyTarget
# Cible de la règle de limitation d'âge appliquée au véhicule.
# Permet de distinguer les limites applicables au tracteur
# et à la citerne.
# -------------------------------------------------------------------
class VehicleAgePolicyTarget(models.TextChoices):
    TRACTOR = "TRACTOR", "Tractor"
    TANKER = "TANKER", "Tanker"

# -------------------------------------------------------------------
# VehicleDocumentType
# Types de documents gérés pour le véhicule, le tracteur ou la citerne.
# -------------------------------------------------------------------
class VehicleDocumentType(models.TextChoices):
    PRODUCT_INSURANCE = "PRODUCT_INSURANCE", "Assurance produit"
    CIVIL_INSURANCE = "CIVIL_INSURANCE", "Assurance responsabilité civile"
    TECHNICAL_INSPECTION = "TECHNICAL_INSPECTION", "Visite technique"
    TANK_CERTIFICATE = "TANK_CERTIFICATE", "Certificat citerne"
    APPROVAL_CERTIFICATE = "APPROVAL_CERTIFICATE", "Agrément"
    REGISTRATION_CERTIFICATE = "REGISTRATION_CERTIFICATE", "Carte grise"
    OTHER = "OTHER", "Autre"


# -------------------------------------------------------------------
# InspectionContext
# Type ou contexte de l’inspection.
# Détermine quelles sections et quels critères apparaissent dans la fiche.
# -------------------------------------------------------------------
class InspectionContext(models.TextChoices):
    DAILY_CHECK = "DAILY_CHECK", "Contrôle quotidien"
    PERIODIC = "PERIODIC", "Periodic"
    BEFORE_TRIP = "BEFORE_TRIP", "Before trip"
    AFTER_INCIDENT = "AFTER_INCIDENT", "After incident"
    AFTER_MAINTENANCE = "AFTER_MAINTENANCE", "After maintenance"

# InspectionStatus
# Represents the lifecycle status of an inspection.
class InspectionStatus(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"

# -------------------------------------------------------------------
# InspectionOverallResult
# Résultat global de toute l’inspection.
# Différent du résultat d’un critère individuel.
# -------------------------------------------------------------------
class InspectionOverallResult(models.TextChoices):
    PASS = "PASS", "Pass"
    FAIL = "FAIL", "Fail"
    PASS_WITH_OBSERVATION = "PASS_WITH_OBSERVATION", "Pass with observation"


# -------------------------------------------------------------------
# InspectionCriterionResultValue
# Résultat d’un critère précis.
# -------------------------------------------------------------------
class InspectionCriterionResultValue(models.TextChoices):
    PASS = "PASS", "Pass"
    FAIL = "FAIL", "Fail"
    NOT_APPLICABLE = "N/A", "Not applicable"

# -------------------------------------------------------------------
# InspectionLocationType
# Type de lieu où l’inspection est effectuée.
# -------------------------------------------------------------------
class InspectionLocationType(models.TextChoices):
    KNOWN = "KNOWN", "Lieu connu"
    CUSTOM = "CUSTOM", "Lieu personnalisé"


# -------------------------------------------------------------------
# DefectCreationSource
# Indique si le défaut a été créé manuellement ou automatiquement.
# -------------------------------------------------------------------

class DefectCreationSource(models.TextChoices):
    SYSTEM = "SYSTEM", "Créé par le système"
    USER = "USER", "Créé par un utilisateur"


# -------------------------------------------------------------------
# DefectStatus
#
# Cycle de vie d’un défaut.
#
# Le statut du défaut représente son état métier réel.
# Il ne décrit pas le traitement de la demande de levée.
#
# CAS 1 — Demande de levée approuvée
# OPEN
#     → Le défaut est actif et bloque potentiellement l’exploitation.
# PENDING_VALIDATION
#     → Une demande de levée a été soumise.
# RELEASED
#     → La demande a été approuvée.
#     → Le défaut ne bloque plus l’exploitation.
#
# Transition :
# OPEN → PENDING_VALIDATION → RELEASED
#
# CAS 2 — Demande de levée rejetée
# OPEN
#     → Le défaut est actif.
# PENDING_VALIDATION
#     → Une demande de levée est en cours d’examen.
# OPEN
#     → La demande a été rejetée.
#     → Le défaut reste actif.
#     → Une nouvelle correction et une nouvelle demande seront nécessaires.
#
# Transition :
# OPEN → PENDING_VALIDATION → OPEN
#
# CAS 3 — Demande de levée annulée
# OPEN
#     → Le défaut est actif.
# PENDING_VALIDATION
#     → Une demande de levée a été soumise.
# OPEN
#     → La demande a été annulée sans décision.
#     → Le défaut reste actif.
#
# Transition :
# OPEN → PENDING_VALIDATION → OPEN
#
# Règle importante :
# RELEASED ne peut être atteint qu’après une validation APPROVED.
# -------------------------------------------------------------------
class DefectStatus(models.TextChoices):
    """Définit les états métier d’un défaut."""

    OPEN = "OPEN", "Open"
    PENDING_VALIDATION = "PENDING_VALIDATION", "Pending validation"
    RELEASED = "RELEASED", "Released"

# -------------------------------------------------------------------
# DefectReleaseRequestStatus
#
# Cycle de vie d’une demande de levée de défaut.
#
# CAS 1 — Demande approuvée
# PENDING
#     → La demande vient d’être soumise.
# COMPLETED
#     → Une DefectReleaseValidation est créée avec decision=APPROVED.
#
# Transition :
# PENDING → COMPLETED
#
# CAS 2 — Demande rejetée
# PENDING
#     → La demande vient d’être soumise.
# COMPLETED
#     → Une DefectReleaseValidation est créée avec decision=REJECTED.
#
# Transition :
# PENDING → COMPLETED
#
# CAS 3 — Demande annulée
# PENDING
#     → La demande a été soumise mais aucune décision n’a été prise.
# CANCELLED
#     → La demande est abandonnée sans validation.
#
# Transition :
# PENDING → CANCELLED
# -------------------------------------------------------------------
class DefectReleaseRequestStatus(models.TextChoices):
    """Définit les états de traitement d’une demande de levée de défaut."""

    PENDING = "PENDING", "Pending"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


# -------------------------------------------------------------------
# ValidationDecision
#
# Décision prise à la fin de l’examen d’une demande de levée.
#
# APPROVED
#     → La demande est acceptée.
#     → DefectReleaseRequest.status devient COMPLETED.
#     → Defect.status devient RELEASED.
#
# REJECTED
#     → La demande est refusée.
#     → DefectReleaseRequest.status devient COMPLETED.
#     → Defect.status revient à OPEN.
#
# La décision ne remplace pas le statut de la demande :
# - le statut indique où en est le traitement ;
# - la décision indique le résultat de ce traitement.
# -------------------------------------------------------------------
class ValidationDecision(models.TextChoices):
    """Définit les décisions possibles après examen d’une demande de levée."""

    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"

# Définit les statuts persistants d’une planification de maintenance.
# Ces statuts décrivent uniquement le cycle de vie métier.
# Les états DUE et OVERDUE restent calculés.
class MaintenanceScheduleStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    FULFILLED = "FULFILLED", "Fulfilled"
    CANCELLED = "CANCELLED", "Cancelled"


# Définit la nature de l’intervention de maintenance.
# Une intervention préventive provient d’une planification.
# Une intervention corrective peut provenir d’un défaut.
class MaintenanceWorkOrderKind(models.TextChoices):
    PREVENTIVE = "PREVENTIVE", "Préventive"
    CORRECTIVE = "CORRECTIVE", "Corrective"

class MaintenanceWorkOrderStatus(models.TextChoices):
    PLANNED = "PLANNED", "Planifié"
    IN_PROGRESS = "IN_PROGRESS", "En cours"
    COMPLETED = "COMPLETED", "Terminé"
    CANCELLED = "CANCELLED", "Annulé"



# -------------------------------------------------------------------
# DowntimeSourceType
# Origine d’une immobilisation opérationnelle.
# -------------------------------------------------------------------
class DowntimeSourceType(models.TextChoices):
    MAINTENANCE = "MAINTENANCE", "Maintenance"
    DEFECT = "DEFECT", "Defect"
    INCIDENT = "INCIDENT", "Incident"
    MANUAL_DECISION = "MANUAL_DECISION", "Manual decision"
    OTHER = "OTHER", "Other"


# -------------------------------------------------------------------
# DowntimeStatus
# Statut d’une immobilisation.
# -------------------------------------------------------------------
class DowntimeStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    ENDED = "ENDED", "Ended"


# -------------------------------------------------------------------
# ReturnToServiceSourceType
# Origine d’une décision de remise en service.
# -------------------------------------------------------------------
class ReturnToServiceSourceType(models.TextChoices):
    DEFECT = "DEFECT", "Defect"
    MAINTENANCE = "MAINTENANCE", "Maintenance"
    DOWNTIME = "DOWNTIME", "Downtime"
    INSPECTOR_DECISION = "INSPECTOR_DECISION", "Inspector decision"
    OTHER = "OTHER", "Other"


# -------------------------------------------------------------------
# ReturnToServiceDecision
# Décision de remise en service.
# PENDING = proposée mais pas encore décidée.
# -------------------------------------------------------------------
class ReturnToServiceDecision(models.TextChoices):
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    PENDING = "PENDING", "Pending"


# -------------------------------------------------------------------
# VehicleAvailabilityResult
# Résultat d’une évaluation de disponibilité.
# -------------------------------------------------------------------
class VehicleAvailabilityResult(models.TextChoices):
    AVAILABLE = "AVAILABLE", "Available"
    NOT_AVAILABLE = "NOT_AVAILABLE", "Not available"


# -------------------------------------------------------------------
# VehicleAvailabilityReasonType
# Raisons normalisées expliquant une disponibilité ou indisponibilité.
# -------------------------------------------------------------------
class VehicleAvailabilityReasonType(models.TextChoices):
    VEHICLE_INACTIVE = "VEHICLE_INACTIVE", "Véhicule inactif"
    ACTIVE_DOWNTIME = "ACTIVE_DOWNTIME", "Immobilisation active"
    OPEN_BLOCKING_DEFECT = "OPEN_BLOCKING_DEFECT", "Défaut bloquant ouvert"
    ACTIVE_TRIP = "ACTIVE_TRIP", "Voyage en cours"


# -------------------------------------------------------------------
# NextTripEligibilityResult
# Résultat d’éligibilité générale pour le prochain voyage.
# -------------------------------------------------------------------
class NextTripEligibilityResult(models.TextChoices):
    ELIGIBLE = "ELIGIBLE", "Eligible"
    NOT_ELIGIBLE = "NOT_ELIGIBLE", "Not eligible"


# -------------------------------------------------------------------
# NextTripEligibilityReasonType
# Raisons normalisées expliquant l’éligibilité ou la non-éligibilité.
# -------------------------------------------------------------------
class NextTripEligibilityReasonType(models.TextChoices):
    NOT_IN_FLEET = "NOT_IN_FLEET", "Not in fleet"
    DOCUMENT_MISSING = "DOCUMENT_MISSING", "Document missing"
    DOCUMENT_EXPIRED = "DOCUMENT_EXPIRED", "Document expired"
    OPEN_BLOCKING_DEFECT = "OPEN_BLOCKING_DEFECT", "Open blocking defect"
    OUT_OF_SERVICE = "OUT_OF_SERVICE", "Out of service"
    RETURN_TO_SERVICE_REQUIRED = "RETURN_TO_SERVICE_REQUIRED", "Return to service required"


# -------------------------------------------------------------------
# EvidenceOwnerType
# Type d’objet auquel une preuve est rattachée.
# Utilisé avec owner_id dans le modèle Evidence.
# -------------------------------------------------------------------
class EvidenceOwnerType(models.TextChoices):
    DOCUMENT = "DOCUMENT", "Document"
    INSPECTION = "INSPECTION", "Inspection"
    INSPECTION_CRITERION_RESULT = "INSPECTION_CRITERION_RESULT", "Inspection criterion result"
    DEFECT = "DEFECT", "Defect"
    CORRECTIVE_ACTION = "CORRECTIVE_ACTION", "Corrective action"
    MAINTENANCE = "MAINTENANCE", "Maintenance"
    RETURN_TO_SERVICE = "RETURN_TO_SERVICE", "Return to service"
    AVAILABILITY_EVALUATION = "AVAILABILITY_EVALUATION", "Availability evaluation"
    NEXT_TRIP_ELIGIBILITY_EVALUATION = "NEXT_TRIP_ELIGIBILITY_EVALUATION", "Next trip eligibility evaluation"


# -------------------------------------------------------------------
# EvidenceType
# Type de preuve conservée.
# -------------------------------------------------------------------
class EvidenceType(models.TextChoices):
    FILE = "FILE", "File"
    PHOTO = "PHOTO", "Photo"
    SIGNATURE = "SIGNATURE", "Signature"
    COMMENT = "COMMENT", "Comment"
    SYSTEM_RECORD = "SYSTEM_RECORD", "System record"






# ---------------------------------------------
# PERMISSIONS
# ---------------------------------------------

# -- UserGroup
class UserGroup:
    INSPECTOR = "Inspector"
    SUPERVISOR = "Supervisor"
    FLEET_MANAGER = "Fleet Manager"
    MANAGER = "Manager"


# InspectionScoringPolicyStatus
# Defines the lifecycle status of a scoring policy.
class InspectionScoringPolicyStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    ACTIVE = "ACTIVE", "Active"
    RETIRED = "RETIRED", "Retired"