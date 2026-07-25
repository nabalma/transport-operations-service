
import uuid
from django.db import models
from apps.fleet.constants import CarrierStatus
from .base import (TimeStampedSoftDeletableModel,)


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

