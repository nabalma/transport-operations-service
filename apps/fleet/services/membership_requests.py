from apps.fleet.constants import CarrierStatus, VehicleMembershipRequestStatus, VehicleMembershipStatus
from apps.fleet.models import Vehicle, VehicleMembership, VehicleMembershipRequest
from apps.fleet.services.vehicles import _get_valid_carrier_or_error, _get_vehicle_or_error, activate_vehicle
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction


"""
++++++++++++++++++++++++++++++++
CREATION DUNE MEMBERSHIP REQUEST
+++++++++++++++++++++++++++++++++
"""


# ---------------------------------------------------
# Vérifie que le véhicule n'appartient pas déjà à la flotte.
# ---------------------------------------------------
def _ensure_vehicle_has_no_active_membership(*, vehicle):
    has_active_membership = VehicleMembership.objects.filter(
        vehicle=vehicle,
        status=VehicleMembershipStatus.ACTIVE,
        exit_date__isnull=True,
        is_deleted=False,
    ).exists()

    if has_active_membership:
        raise ValidationError(
            {"vehicle": "Ce véhicule appartient déjà à la flotte."}
        )


# -------------------------------------------------------------------
# Vérifie qu'aucune demande ouverte n'existe déjà pour le véhicule.
# -------------------------------------------------------------------
def _ensure_vehicle_has_no_open_request(*, vehicle):
    has_open_request = VehicleMembershipRequest.objects.filter(
        vehicle=vehicle,
        status__in=[
            VehicleMembershipRequestStatus.DRAFT,
            VehicleMembershipRequestStatus.PENDING,
        ],
        is_deleted=False,
    ).exists()

    if has_open_request:
        raise ValidationError(
            {
                "vehicle": (
                    "Une demande d'appartenance est déjà "
                    "en cours pour ce véhicule."
                )
            }
        )


# -------------------------------------------------------------------
# Crée une demande d'appartenance d'un véhicule à la flotte.
#
# Étapes :
# 1. Récupérer le véhicule.
# 2. Vérifier qu'il n'est pas déjà dans la flotte.
# 3. Vérifier qu'il n'a pas déjà une demande ouverte.
# 4. Vérifier que son transporteur est valide.
# 5. Créer et retourner la demande.
# -------------------------------------------------------------------
def create_vehicle_membership_request(*,vehicle_id,requested_entry_date,membership_type,created_by,):

    vehicle = _get_vehicle_or_error(vehicle_id=vehicle_id)
    _ensure_vehicle_has_no_active_membership(vehicle=vehicle)
    _ensure_vehicle_has_no_open_request(vehicle=vehicle)
    _get_valid_carrier_or_error(vehicle=vehicle)

    return VehicleMembershipRequest.objects.create(
        vehicle=vehicle,
        requested_entry_date=requested_entry_date,
        membership_type=membership_type,
        created_by=created_by,
        updated_by=created_by,
    )



"""
++++++++++++++++++++++++++++++++
SOUMISSION DUNE MEMBERSHIP REQUEST
+++++++++++++++++++++++++++++++++
"""

# -------------------------------------------------------------------
# Récupère une demande existante et non supprimée.
# -------------------------------------------------------------------
def _get_membership_request_or_error(*, membership_request_id):
    membership_request = VehicleMembershipRequest.objects.filter(
        id=membership_request_id,
        is_deleted=False,
    ).first()

    if membership_request is None:
        raise ValidationError(
            {
                "membership_request": (
                    "Cette demande n'existe pas ou a été supprimée."
                )
            }
        )

    return membership_request

# -------------------------------------------------------------------
# Vérifie qu'une demande peut être soumise.
# -------------------------------------------------------------------
def _ensure_request_can_be_submitted(*, membership_request):
    if membership_request.status != VehicleMembershipRequestStatus.DRAFT:
        raise ValidationError(
            {
                "status": (
                    "Seules les demandes en statut DRAFT "
                    "peuvent être soumises."
                )
            }
        )
    

def _notify_manager_membership_request_submitted(*,membership_request,):
    ...
    
# -------------------------------------------------------------------
# Soumet une demande d'appartenance à la flotte.
#
# Étapes :
# 1. Récupérer la demande.
# 2. Vérifier qu'elle peut être soumise.
# 3. Passer son statut à PENDING.
# 4. Enregistrer l'utilisateur ayant fait la modification.
# 5. Sauvegarder et retourner la demande.
# -------------------------------------------------------------------
def submit_vehicle_membership_request(*,membership_request_id,submitted_by,):
    membership_request = _get_membership_request_or_error(membership_request_id=membership_request_id,)
    _ensure_request_can_be_submitted(membership_request=membership_request,)
    membership_request.status = VehicleMembershipRequestStatus.PENDING
    membership_request.updated_by = submitted_by
    membership_request.save(update_fields=["status","updated_by","updated_at",])

    #Si le save a marché, envoyer le email en asynchrone
    _notify_manager_membership_request_submitted(membership_request=membership_request,)

    return membership_request



# -------------------------------------------------------------------
# Soumet une demande d'appartenance à la flotte.
#
# Étapes :
# 1. Récupérer la demande.
# 2. Vérifier qu'elle peut être soumise.
# 3. Passer son statut à PENDING.
# 4. Enregistrer l'utilisateur ayant fait la modification.
# 5. Sauvegarder et retourner la demande.
# -------------------------------------------------------------------
def delete_vehicle_membership_request(*,membership_request_id,deleted_by,):
    membership_request = _get_membership_request_or_error(membership_request_id=membership_request_id,)
    
    _ensure_request_can_be_submitted(membership_request=membership_request,)
    membership_request.is_deleted=True
    membership_request.status = VehicleMembershipRequestStatus.CANCELLED
    membership_request.updated_by = deleted_by
    membership_request.deleted_by = deleted_by
    membership_request.save(update_fields=["is_deleted","status","updated_by","updated_at","deleted_by","deleted_at"])

    #Si le save a marché, envoyer le email en asynchrone
    _notify_manager_membership_request_submitted(membership_request=membership_request,)

    return membership_request



"""
+++++++++++++++++++++++++++++++++++++++++++++++++++
CANCELLATION DUNE SOUMISSION DUNE MEMBERSHIP 
++++++++++++++++++++++++++++++++++++++++++++++++++
"""



def _ensure_request_can_be_cancelled(*, membership_request):
    if membership_request.status != VehicleMembershipRequestStatus.DRAFT:
        raise ValidationError(
            {
                "status": (
                    "Seules les demandes en statut DRAFT "
                    "peuvent être annulées."
                )
            }
        )
    
# -------------------------------------------------------------------
# Annule une demande d'appartenance à la flotte.
#
# Étapes :
# 1. Récupérer la demande.
# 2. Vérifier qu'elle peut être annulée.
# 3. Passer son statut à CANCELLED.
# 4. Enregistrer l'utilisateur ayant effectué l'annulation.
# 5. Sauvegarder la demande.
# 6. Notifier les parties concernées si nécessaire.
# -------------------------------------------------------------------
def cancel_vehicle_membership_request(*,membership_request_id,cancelled_by,):
    membership_request = _get_membership_request_or_error(membership_request_id=membership_request_id,)

    _ensure_request_can_be_cancelled(membership_request=membership_request,)
    membership_request.status = VehicleMembershipRequestStatus.CANCELLED
    membership_request.updated_by = cancelled_by
    membership_request.save(update_fields=["status","updated_by","updated_at",])

    # Si la sauvegarde a réussi, notifier les parties concernées.
    # _notify_managers_membership_request_cancelled(membership_request=membership_request,# )
    #_notifiy_le_superviseur lui meme

    return membership_request




"""
+++++++++++++++++++++++++++++++++++++++++++++++++++
APPROBATION DUNE SOUMISSION DUNE MEMBERSHIP 
++++++++++++++++++++++++++++++++++++++++++++++++++
"""

# -------------------------------------------------------------------
# Vérifie qu'une demande peut être approuvée.
# Seules les demandes en statut PENDING peuvent être approuvées.
# -------------------------------------------------------------------
def _ensure_request_can_be_approved(*, membership_request):
    if membership_request.status != VehicleMembershipRequestStatus.PENDING:
        raise ValidationError(
            {
                "status": (
                    "Seules les demandes en statut PENDING "
                    "peuvent être approuvées."
                )
            }
        )




# -------------------------------------------------------------------
# Approuve une demande d'appartenance d'un véhicule à la flotte.
#
# Étapes :
# 1. Récupérer la demande existante et non supprimée.
# 2. Vérifier que la demande est en statut PENDING.
# 3. Vérifier que le véhicule existe toujours et n'est pas supprimé.
# 4. Vérifier que le véhicule n'a pas déjà une appartenance active.
# 5. Vérifier que le transporteur associé au véhicule est toujours actif.
# 6. Créer le VehicleMembership correspondant à la demande.
# 7. Passer la demande au statut APPROVED.
# 8. Enregistrer le manager ayant pris la décision.
# 9. Enregistrer la date, le commentaire et l'utilisateur de modification.
# 10. Sauvegarder la demande et retourner le résultat de l'approbation.
# -------------------------------------------------------------------
@transaction.atomic
def approve_vehicle_membership_request(*,membership_request_id,approved_by,decision_comment=None,):
    membership_request = _get_membership_request_or_error(membership_request_id=membership_request_id,)

    _ensure_request_can_be_approved(membership_request=membership_request,)
    vehicle = _get_vehicle_or_error(vehicle_id=membership_request.vehicle_id,)
    _ensure_vehicle_has_no_active_membership(vehicle=vehicle,)
    carrier = _get_valid_carrier_or_error(vehicle=vehicle,)

    VehicleMembership.objects.create(
    vehicle=vehicle,
    carrier=carrier,
    entry_date=membership_request.requested_entry_date,
    membership_type=membership_request.membership_type,
    status=VehicleMembershipStatus.ACTIVE,
    created_by=approved_by,
    updated_by=approved_by,)

    membership_request.status = VehicleMembershipRequestStatus.APPROVED
    membership_request.decided_by = approved_by
    membership_request.decided_at = timezone.now()
    membership_request.decision_comment = decision_comment
    membership_request.updated_by = approved_by

    activate_vehicle(vehicle=vehicle,updated_by=approved_by,)

    membership_request.save(
    update_fields=[
        "status",
        "decided_by",
        "decided_at",
        "decision_comment",
        "updated_by",
        "updated_at",
    ])

    return membership_request



"""
+++++++++++++++++++++++++++++++++++++++++++++++++++
REJET DUNE SOUMISSION DUNE MEMBERSHIP 
++++++++++++++++++++++++++++++++++++++++++++++++++
"""

# -------------------------------------------------------------------
# Vérifie qu'une demande peut être rejetée.
# Seules les demandes en statut PENDING peuvent être rejetées.
# -------------------------------------------------------------------
def _ensure_request_can_be_rejected(*, membership_request):
    if membership_request.status != VehicleMembershipRequestStatus.PENDING:
        raise ValidationError(
            {
                "status": (
                    "Seules les demandes en statut PENDING "
                    "peuvent être rejetées."
                )
            }
        )
    
# -------------------------------------------------------------------
# Rejette une demande d'appartenance d'un véhicule à la flotte.
#
# Étapes :
# 1. Récupérer la demande existante et non supprimée.
# 2. Vérifier que la demande est en statut PENDING.
# 3. Passer la demande au statut REJECTED.
# 4. Enregistrer le manager ayant pris la décision.
# 5. Enregistrer la date et le commentaire de la décision.
# 6. Enregistrer l'utilisateur ayant effectué la modification.
# 7. Sauvegarder et retourner la demande rejetée.
# -------------------------------------------------------------------
@transaction.atomic
def reject_vehicle_membership_request(*,membership_request_id,rejected_by,decision_comment=None,):
    membership_request = _get_membership_request_or_error(membership_request_id=membership_request_id,)

    _ensure_request_can_be_rejected(membership_request=membership_request,)

    membership_request.status = VehicleMembershipRequestStatus.REJECTED
    membership_request.decided_by = rejected_by
    membership_request.decided_at = timezone.now()
    membership_request.decision_comment = decision_comment
    membership_request.updated_by = rejected_by

    membership_request.save(
        update_fields=[
            "status",
            "decided_by",
            "decided_at",
            "decision_comment",
            "updated_by",
            "updated_at",
        ]
    )

    return membership_request