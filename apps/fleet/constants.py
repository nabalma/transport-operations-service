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

# -------------------------------------------------------------------
# InspectionLocationType
# Type de lieu où l’inspection est effectuée.
# -------------------------------------------------------------------
class InspectionLocationType(models.TextChoices):
    KNOWN = "KNOWN", "Lieu connu"
    CUSTOM = "CUSTOM", "Lieu personnalisé"


# -------------------------------------------------------------------
# DefectSourceType
# Origine d’un défaut/anomalie.
# -------------------------------------------------------------------
class DefectSourceType(models.TextChoices):
    INSPECTION = "INSPECTION", "Inspection"
    OBSERVATION = "OBSERVATION", "Observation"
    INCIDENT = "INCIDENT", "Incident"
    MAINTENANCE = "MAINTENANCE", "Maintenance"


# -------------------------------------------------------------------
# DefectSeverity
# Gravité du défaut.
# La gravité n’est pas forcément équivalente au caractère bloquant.
# -------------------------------------------------------------------
class DefectSeverity(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"
    CRITICAL = "CRITICAL", "Critical"


# -------------------------------------------------------------------
# DefectStatus
# Cycle de vie d’un défaut.
# OPEN = défaut ouvert.
# CORRECTED = correction déclarée.
# PENDING_VALIDATION = correction en attente de validation.
# RELEASED = blocage levé.
# CLOSED = dossier clôturé.
# -------------------------------------------------------------------
class DefectStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    CORRECTED = "CORRECTED", "Corrected"
    PENDING_VALIDATION = "PENDING_VALIDATION", "Pending validation"
    RELEASED = "RELEASED", "Released"
    CLOSED = "CLOSED", "Closed"


# -------------------------------------------------------------------
# CorrectiveActionStatus
# Statut d’une action corrective.
# -------------------------------------------------------------------
class CorrectiveActionStatus(models.TextChoices):
    PLANNED = "PLANNED", "Planned"
    DONE = "DONE", "Done"
    CANCELLED = "CANCELLED", "Cancelled"


# -------------------------------------------------------------------
# ValidationDecision
# Décision de validation, notamment pour la levée d’un blocage.
# -------------------------------------------------------------------
class ValidationDecision(models.TextChoices):
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


# -------------------------------------------------------------------
# MaintenanceType
# Type de maintenance.
# -------------------------------------------------------------------
class MaintenanceType(models.TextChoices):
    PREVENTIVE = "PREVENTIVE", "Preventive"
    CORRECTIVE = "CORRECTIVE", "Corrective"


# -------------------------------------------------------------------
# MaintenanceStatus
# Cycle de vie d’une maintenance.
# -------------------------------------------------------------------
class MaintenanceStatus(models.TextChoices):
    PLANNED = "PLANNED", "Planned"
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


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


# ---------------------------------------------
# APPROBATION
# ---------------------------------------------
