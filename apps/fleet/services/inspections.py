from rest_framework.exceptions import ValidationError
from django.db import transaction

from apps.fleet.models import InspectionVersion


INITIAL_VERSION = "0.0.0"

#   Crée une version d'inspection en appliquant les règles métier.
#    Règles métier :
#    - la version 0.0.0 peut ne pas avoir de source_version ; Sa source_version est nulle
#    - toute autre version doit avoir une source_version ;
#    - la source_version doit appartenir au même contexte.
@transaction.atomic
def create_inspection_version(*,context: str,version: str,source_version: InspectionVersion | None, is_current: bool,created_by,) -> InspectionVersion:
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

    return InspectionVersion.objects.create(
        context=context,
        version=version,
        source_version=source_version,
        is_current=is_current,
        created_by=created_by,
    )

def update_inspection_version_status(*,inspection_version: InspectionVersion,is_current: bool,updated_by,) -> InspectionVersion:
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