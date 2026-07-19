from datetime import date

from apps.fleet.constants import InspectionContext
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch, QuerySet
from io import BytesIO
from reportlab.pdfgen import canvas

from apps.fleet.models import Inspection, InspectionContextVersion, InspectionCriterion, InspectionSection, Vehicle

# =======================================
# ENREGISTRER UNE VERSION
# =======================================

INITIAL_VERSION = "0.0.0"

#   Crée une version d'inspection en appliquant les règles métier.
#    Règles métier :
#    - la version 0.0.0 peut ne pas avoir de source_version ; Sa source_version est nulle
#    - toute autre version doit avoir une source_version ;
#    - la source_version doit appartenir au même contexte.
@transaction.atomic
def create_inspection_version(*,context: str,version: str,source_version: InspectionContextVersion | None, is_current: bool,created_by,) -> InspectionContextVersion:
    """
    Crée une nouvelle version d'inspection.
    Règles métier :
    - la version 0.0.0 doit toujours avoir source_version=None ;
    - toute autre version doit avoir une source_version ;
    - la source_version doit appartenir au même contexte ;
    - is_current est défini explicitement par l'utilisateur.
    Retourne :
        L'instance InspectionVersion créée.
    """
    if version == INITIAL_VERSION and source_version is not None:
        raise ValidationError(
            {
                "source_version": (
                    "La version 0.0.0 ne peut pas avoir de version source."
                )
            }
        )
    else :

        if source_version is None:
            raise ValidationError(
                {
                    "source_version": (
                        "Une version source est obligatoire pour toute version "
                        "différente de 0.0.0."
                    )
                }
            )

        if source_version.context != context :
            raise ValidationError(
                {
                    "source_version": (
                        "La version source doit appartenir au même contexte d'inspection "
                        "que la nouvelle version."
                    )
                }
            )
        
        # Si cette version devient la version courante,
    # on retire ce statut aux autres versions du même contexte.
    if is_current:
        InspectionContextVersion.objects.filter(
            context=context,
            is_current=True,
            ).update(
            is_current=False,
            updated_by=created_by,
        )

    # Création de la nouvelle version
    return InspectionContextVersion.objects.create(
        context=context,
        version=version,
        source_version=source_version,
        is_current=is_current,
        created_by=created_by,
    )


# =======================================
# METTRE A JOUR LE STATUS DUNE VERSION
# =======================================

def update_inspection_version_status(*,inspection_version: InspectionContextVersion,is_current: bool,updated_by,) -> InspectionContextVersion:
    """
    Met à jour uniquement le statut is_current d'une version d'inspection.
    Les champs context, version et source_version restent immuables.
    Args:
        inspection_version:
            Version d'inspection à modifier.
        is_current:
            Nouvelle valeur du statut courant.
        updated_by:
            Utilisateur à l'origine de la modification.
    Retourne :
        L'instance InspectionVersion mise à jour.
    """
    inspection_version.is_current = is_current
    inspection_version.updated_by = updated_by

    inspection_version.save(
        update_fields=[
            "is_current",
            "updated_by",
            "updated_at",
        ]
    )

    return inspection_version 



# =======================================
# GENERER UNE FICHE DINSPECTION
# =======================================


# -------------------------------------------------------------------
# _get_current_inspection_version
# Retourne la version courante du formulaire pour un type d’inspection.
# -------------------------------------------------------------------
def _get_current_inspection_version(*,inspection_type: str,) -> InspectionContextVersion:
    try:
        return InspectionContextVersion.objects.get(
            context=inspection_type,
            is_current=True,
            is_deleted=False,)

    except InspectionContextVersion.DoesNotExist as exc:
        raise ValidationError(
            {
                "inspection_type": (
                    "Aucune version courante n’existe pour ce type "
                    "d’inspection."
                )
            }
        ) from exc

# -------------------------------------------------------------------
# _validate_inspection_type
# Vérifie que le type d’inspection demandé est autorisé.
# -------------------------------------------------------------------
def _validate_inspection_type(*,inspection_type: str,) -> None:
    valid_values = {
        choice.value
        for choice in InspectionContext
    }

    if inspection_type not in valid_values:
        raise ValidationError(
            {
                "inspection_type": (
                    "Le type d’inspection fourni est invalide."
                )
            }
        )


def generate_inspection_sheet(*,vehicle: Vehicle,inspection_type: str,inspection_date: date,location_type: str,location_name: str,created_by,) -> bytes:
    """
    Génère une fiche d’inspection vierge pour un véhicule.
    La fiche utilise la version courante du formulaire correspondantau type d’inspection demandé.
    Cette fonction ne crée pas encore une Inspection en base de données. Elle prépare et retourne le contenu du document PDF.

    Args:
        vehicle:Véhicule concerné par la fiche.
        inspection_type:Type d’inspection demandé, par exemple DAILY_CHECK.
        inspection_date:Date prévue pour l’inspection.
        location_type:Type du lieu d’inspection : KNOWN ou CUSTOM.
        location_name:Nom du lieu où l’inspection sera effectuée.
        created_by:Utilisateur ayant demandé la génération de la fiche.

    Returns:
        
    Raises:
        ValidationError:
            Si les données métier sont invalides.

        InspectionContextVersion.DoesNotExist:
            Si aucune version courante n’existe pour ce type
            d’inspection.
    """

    _validate_inspection_type(inspection_type=inspection_type,)
    inspection_version = _get_current_inspection_version(inspection_type=inspection_type,)
    inspection_version=inspection_version,


    return 
  
    

 
