from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.fleet.constants import (DefectCreationSource, DefectReleaseRequestStatus, DefectStatus,)
from apps.fleet.models import Defect, DefectReleaseRequest


# -------------------------------------------------------------------
# create_system_defect
# Crée un défaut généré automatiquement par le système.
#
# Cette fonction est responsable uniquement de la création du Defect.
# Elle ne décide pas si un résultat d’inspection doit générer un défaut.
# -------------------------------------------------------------------
def create_system_defect(
    *,
    vehicle,
    description,
    user,
    source_inspection=None,
    source_inspection_criterion_result=None,
):
    """
    Create and return a system-generated defect.

    The caller is responsible for validating whether the source event
    is allowed to generate a defect.
    """
    defect = Defect(
        vehicle=vehicle,
        creation_source=DefectCreationSource.SYSTEM,
        source_inspection=source_inspection,
        source_inspection_criterion_result=(
            source_inspection_criterion_result
        ),
        description=description,
        created_by=user,
        updated_by=user,
    )

    try:
        defect.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict) from exc

    defect.save()

    return defect


# _ensure_can_submit_defect_release_request
# Vérifie qu’un défaut peut recevoir une demande de levée.
def _ensure_can_submit_defect_release_request(
    *,
    defect,
    correction_summary: str,
) -> None:
    """
    Valide les règles métier nécessaires avant la soumission
    d’une demande de levée de défaut.
    """

    if defect.is_deleted:
        raise ValidationError(
            {
                "defect": (
                    "A deleted defect cannot receive a release request."
                )
            }
        )

    if defect.status != DefectStatus.OPEN:
        raise ValidationError(
            {
                "status": (
                    "Only an open defect can receive a release request."
                )
            }
        )

    has_pending_request = DefectReleaseRequest.objects.filter(
        defect=defect,
        status=DefectReleaseRequestStatus.PENDING,
        is_deleted=False,
    ).exists()

    if has_pending_request:
        raise ValidationError(
            {
                "defect": (
                    "This defect already has a pending release request."
                )
            }
        )

    if not correction_summary or not correction_summary.strip():
        raise ValidationError(
            {
                "correction_summary": (
                    "The correction summary cannot be empty."
                )
            }
        )


# _mark_defect_as_pending_validation
# Place un défaut en attente de validation.
def _mark_defect_as_pending_validation(
    *,
    defect,
    user,
) -> None:
    """
    Met à jour le statut du défaut vers PENDING_VALIDATION
    et enregistre l’utilisateur à l’origine du changement.
    """
    defect.status = DefectStatus.PENDING_VALIDATION
    defect.updated_by = user

    defect.save(
        update_fields=[
            "status",
            "updated_by",
            "updated_at",
        ]
    )



# submit_defect_release_request
# Soumet une demande de levée pour un défaut corrigé.
@transaction.atomic
def submit_defect_release_request(
    *,
    defect: Defect,
    correction_summary: str,
    submitted_by,
) -> DefectReleaseRequest:
    """
    Soumet une demande de levée et place le défaut
    en attente de validation.
    """
    defect = (
    Defect.objects
    .select_for_update()
    .get(pk=defect.pk)
    )
    
    _ensure_can_submit_defect_release_request(
        defect=defect,
        correction_summary=correction_summary,
    )

    release_request = DefectReleaseRequest.objects.create(
        defect=defect,
        correction_summary=correction_summary.strip(),
        submitted_by=submitted_by,
        created_by=submitted_by,
        updated_by=submitted_by,
    )

    _mark_defect_as_pending_validation(
        defect=defect,
        user=submitted_by,
    )

    return release_request