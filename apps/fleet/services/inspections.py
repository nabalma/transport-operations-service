from datetime import date

from apps.fleet.constants import InspectionContext
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch, QuerySet
from io import BytesIO
from reportlab.pdfgen import canvas

from apps.fleet.models import Inspection, InspectionVersion, InspectionCriterion, InspectionSection, Vehicle

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
    if version == INITIAL_VERSION :
        if source_version is not None:
            raise ValidationError(
            {
                "source_version": (
                    "La version 0.0.0 ne peut pas avoir de version source."
                )
            })
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
        InspectionVersion.objects.filter(
            context=context,
            is_current=True,
            ).update(
            is_current=False,
            updated_by=created_by,
        )

    # Création de la nouvelle version
    return InspectionVersion.objects.create(
        context=context,
        version=version,
        source_version=source_version,
        is_current=is_current,
        created_by=created_by,
    )


# =======================================
# METTRE A JOUR LE STATUS DUNE VERSION
# =======================================

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



# =======================================
# GENERER UNE FICHE DINSPECTION
# =======================================

# _validate_inspection_context
# Vérifie que le contexte d’inspection fourni est autorisé.
# Lève une erreur de validation lorsque le contexte est absent ou invalide.
def _validate_inspection_context(*,inspection_context: str | None,) -> None:
    """
    Valide le contexte utilisé pour générer la fiche d’inspection.
    Lève une erreur lorsqu’aucun contexte ne correspond.
    """

    valid_contexts = {choice.value for choice in InspectionContext}

    if inspection_context not in valid_contexts:
        raise ValidationError(
            {
                "context": (
                    "Le contexte d’inspection fourni est absent ou invalide."
                )
            }
        )


# _get_current_inspection_version
# Recherche la version courante du formulaire pour le contexte demandé.
# Les versions supprimées sont automatiquement exclues.
def _get_current_inspection_version(*,inspection_context: str,) -> InspectionVersion:
    """
    Retourne la version courante d’un contexte d’inspection.
    Lève une erreur lorsqu’aucune version courante n’est disponible.
    """

    inspection_version = (
        InspectionVersion.objects
        .filter(
            context=inspection_context,
            is_current=True,
            is_deleted=False,
        )
        .order_by("-created_at")
        .first()
    )

    if inspection_version is None:
        raise ValidationError(
            {
                "context": (
                    "Aucune version courante n’existe pour ce contexte "
                    "d’inspection."
                )
            }
        )

    return inspection_version

# build_inspection_header
# Construit les informations d’en-tête de la fiche d’inspection.
# Les données absentes sont retournées avec la valeur None.
def build_inspection_header(
    *,
    vehicle: Vehicle | None = None,
    inspection_date: date | None = None,
    location_name: str | None = None,
    driver_name: str | None = None,
    inspector_name: str | None = None,
) -> dict:
    """
    Construit les données d’en-tête d’une fiche d’inspection.

    Cette fonction ne crée ni ne modifie aucune donnée en base.
    """

    return {
        "location_name": location_name,
        "vehicle_registration": (
            vehicle.display_registration
            if vehicle
            else None
        ),
        "driver_name": driver_name,
        "carrier_name": (
            vehicle.carrier.name
            if vehicle
            else None
        ),
        "inspection_date": inspection_date,
        "inspector_name": inspector_name,
    }

# build_inspection_sections
# Construit les sections liées à la version d’inspection sélectionnée.
# Chaque section contient uniquement ses critères actifs.
def build_inspection_sections(
    *,
    inspection_version: InspectionVersion,
) -> list[dict]:
    """
    Construit les sections de la fiche d’inspection vierge.

    Les sections supprimées sont exclues du résultat.
    """

    sections = inspection_version.sections.filter(
        is_deleted=False,
    ).order_by("reference")

    return [
        {
          #  "id": str(section.id),
            "reference": section.reference,
          #  "code": section.code,
            "title": section.title,
            "criterias": build_section_criteria(
                section=section,
            ),
        }
        for section in sections
    ]


# build_section_criteria
# Construit les critères actifs liés à une section d’inspection.
# Les critères supprimés ou inactifs sont exclus du résultat.
def build_section_criteria(*,section: InspectionSection,) -> list[dict]:
    """
    Construit les critères actifs d’une section d’inspection.
    Les résultats restent vides pour une fiche d’inspection vierge.
    """

    criteria = section.criteria.filter(is_deleted=False,is_active=True,).order_by("reference")

    return [
        {
          "reference": criterion.reference,
            "label": criterion.label,
        }
        for criterion in criteria
    ]



# build_blank_inspection_sheet
# Construit une fiche d’inspection vierge à partir d’une version donnée.
# Les informations d’en-tête peuvent être fournies ou laissées vides.
def build_blank_inspection_sheet(
    *,
    inspection_context: str | None,
    vehicle: Vehicle | None = None,
    inspection_date: date | None = None,
    location_name: str | None = None,
    driver_name: str | None = None,
    inspector_name: str | None = None,
) -> dict:
    """
    Construit les données d’une fiche d’inspection vierge.
    Cette fonction orchestre la validation, la recherche de la version
    courante et la construction de l’en-tête.
    """

    _validate_inspection_context(inspection_context=inspection_context,)

    inspection_version = _get_current_inspection_version(inspection_context=inspection_context,)

    header = build_inspection_header(
        vehicle=vehicle,
        inspection_date=inspection_date,
        location_name=location_name,
        driver_name=driver_name,
        inspector_name=inspector_name,
    )
    sections = build_inspection_sections(inspection_version=inspection_version,)


    return {
        "inspection_version": str(inspection_version.id),
        "inspection_context": inspection_version.context,
        "version": inspection_version.version,
        "header": header,
        "sections": sections,
        
       
    }

 
