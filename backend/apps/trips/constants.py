from django.db import models


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

