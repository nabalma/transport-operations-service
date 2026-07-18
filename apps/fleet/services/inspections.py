from apps.fleet.constants import InspectionContext
from rest_framework.exceptions import ValidationError
from django.db import transaction

from apps.fleet.models import Inspection, InspectionContextVersion, Vehicle


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


def _validate_inspection_type(inspection_type: str,) -> None:
    """
    Vérifie que le type d’inspection demandé est supporté.
    Args:
        inspection_type: Type d’inspection à valider.
    Raises:
        ValidationError: Si le type d’inspection est invalide.
    """
    valid_types = InspectionContext.values

    if inspection_type not in valid_types:
        raise ValidationError(
            {
                "inspection_type": (
                    f"Type d’inspection invalide : {inspection_type}."
                )
            }
        )



def generate_inspection_sheet(*,vehicle: Vehicle,inspection_type: InspectionContext,inspector_name: str,created_by,) -> Inspection:
    """
    Génère une fiche d’inspection pour un véhicule.
    La fiche est créée à partir de la version courante du modèle
    correspondant au type d’inspection demandé.
    Args:
        vehicle: Véhicule à inspecter.
        inspection_type: Type d’inspection à effectuer.
        inspector_name: Nom de la personne qui réalisera l’inspection.
        created_by: Utilisateur ayant généré la fiche.
    Returns:
        L’inspection créée et associée à la version courante du modèle.
    Raises:
        ValidationError: Si le type d’inspection est invalide.
        InspectionContextVersion.DoesNotExist:
            Si aucune version courante n’existe pour ce type d’inspection.
    """
    _validate_inspection_type(inspection_type)
    raise NotImplementedError