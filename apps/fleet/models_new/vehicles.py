from django.utils import timezone
import uuid

from django.conf import settings
from django.db import models


from apps.fleet.upload_paths import vehicle_document_upload_path
from apps.fleet.constants import  VehicleAgePolicyTarget, VehicleDocumentType, VehicleMembershipRequestStatus, VehicleMembershipStatus, VehicleMembershipType, VehicleScope, VehicleStatus  

from .base import TimeStampedSoftDeletableModel
from .carriers import Carrier

# -------------------------------------------------------------------
# VehicleAgePolicyConfiguration
# Configuration des limites d'âge applicables aux véhicules.
# Chaque nouvelle configuration conserve l'historique des anciennes
# limites grâce à sa période d'application.
# -------------------------------------------------------------------
class VehicleAgePolicyConfiguration(TimeStampedSoftDeletableModel):
    target = models.CharField(max_length=20,choices=VehicleAgePolicyTarget.choices,)
    maximum_allowed_age = models.PositiveSmallIntegerField()
    effective_from = models.DateTimeField()
    effective_to = models.DateTimeField(blank=True,null=True,)

    class Meta:
        constraints = [ 
            models.UniqueConstraint(
            fields=["target", "effective_from"],
            name="unique_vehicle_age_policy_period",
        ),]


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

    # Année de fabrication du tracteur, rendu obligatoire a la creation du camion. 
    tractor_manufacture_year = models.PositiveSmallIntegerField()

    # Immatriculation de la citerne. rendu obligatoire a la creation du camion
    tanker_registration = models.CharField(max_length=50)

      # Année de fabrication de la citerne,
    tanker_manufacture_year = models.PositiveSmallIntegerField()


    # Immatriculation affichée : tracteur / citerne. Calculée dans save().
    display_registration = models.CharField(max_length=120, editable=False)

    # Date de début de l’attelage tracteur + citerne.
    vehicle_coupling_start_date = models.DateField()

    # Date de fin de cet attelage. Null signifie attelage actif.
    vehicle_coupling_end_date = models.DateField(blank=True, null=True)

    # Statut général. Ne remplace pas l’éligibilité ni la disponibilité.
    status = models.CharField(max_length=30, choices=VehicleStatus.choices, default=VehicleStatus.AWAITING_FLEET_ENTRY)

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

    @property
    def carrier(self):
        return self.vehicle.carrier

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
