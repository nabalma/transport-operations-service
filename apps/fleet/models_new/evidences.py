
import uuid
from django.db import models


from .base import TimeStampedSoftDeletableModel
from apps.fleet.constants import EvidenceOwnerType, EvidenceType

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
    
