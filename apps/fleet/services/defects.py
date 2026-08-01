from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.fleet.constants import (DefectCreationSource, DefectReleaseRequestStatus, DefectStatus, MaintenanceWorkOrderKind, MaintenanceWorkOrderStatus, ValidationDecision,)
from apps.fleet.models import MaintenanceWorkOrder, Defect, DefectReleaseRequest,DefectReleaseValidation


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


# ensure_defect_is_open
# Vérifie qu’un défaut existe encore et qu’il est ouvert.
def ensure_defect_is_open(
    *,
    defect: Defect,
) -> None:
    """
    Vérifie qu’un défaut est non supprimé et en statut OPEN.
    """

    if defect.is_deleted:
        raise ValidationError(
            {
                "defect": (
                    "Un défaut supprimé ne peut pas être utilisé."
                )
            }
        )

    if defect.status != DefectStatus.OPEN:
        raise ValidationError(
            {
                "status": (
                    "Seul un défaut ouvert peut être utilisé."
                )
            }
        )




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

    ensure_defect_is_open(
    defect=defect,
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





# _defect_has_completed_work_order
# Indique si un défaut possède au moins un ordre correctif terminé.
def _defect_has_completed_work_order(
    *,
    defect: Defect,
) -> bool:
    """
    Retourne True si le défaut possède au moins un ordre
    de travail correctif terminé.
    """

    return MaintenanceWorkOrder.objects.filter(
        defect=defect,
        kind=MaintenanceWorkOrderKind.CORRECTIVE,
        status=MaintenanceWorkOrderStatus.COMPLETED,
        is_deleted=False,
    ).exists()


# _ensure_defect_has_completed_work_order
# Vérifie qu’un défaut possède un ordre correctif terminé.
def _ensure_defect_has_completed_work_order(
    *,
    defect: Defect,
) -> None:
    """
    Empêche la soumission d’une demande de levée
    tant qu’aucun ordre correctif lié au défaut n’est terminé.
    """

    if not _defect_has_completed_work_order(
        defect=defect,
    ):
        raise ValidationError(
            {
                "defect": (
                    "Une demande de levée ne peut être soumise "
                    "qu’après la fin d’un ordre de travail correctif."
                )
            }
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

    _ensure_defect_has_completed_work_order(
    defect=defect,
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


# _ensure_can_validate_defect_release_request
# Vérifie qu’une demande de levée peut recevoir une décision.
def _ensure_can_validate_defect_release_request(
    *,
    release_request,
    decision: str,
    comment: str | None,
) -> None:
    """
    Valide les règles métier avant la création d’une décision finale.
    """
    if release_request.is_deleted:
        raise ValidationError(
            {
                "release_request": (
                    "A deleted release request cannot be validated."
                )
            }
        )

    if release_request.status != DefectReleaseRequestStatus.PENDING:
        raise ValidationError(
            {
                "status": (
                    "Only a pending release request can be validated."
                )
            }
        )

    if decision not in ValidationDecision.values:
        raise ValidationError(
            {
                "decision": (
                    "The decision must be APPROVED or REJECTED."
                )
            }
        )

    if (
        decision == ValidationDecision.REJECTED
        and (not comment or not comment.strip())
    ):
        raise ValidationError(
            {
                "comment": (
                    "A comment is required when the request is rejected."
                )
            }
        )

    if release_request.defect.status != DefectStatus.PENDING_VALIDATION:
        raise ValidationError(
            {
                "defect": (
                    "The related defect must be pending validation."
                )
            }
        )

    validation_exists = DefectReleaseValidation.objects.filter(
        release_request=release_request,
    ).exists()

    if validation_exists:
        raise ValidationError(
            {
                "release_request": (
                    "This release request has already been validated."
                )
            }
        )


# _mark_release_request_as_completed
# Marque une demande de levée comme terminée.
def _mark_release_request_as_completed(
    *,
    release_request,
    user,
) -> None:
    """
    Met à jour la demande de levée après une décision finale.
    """
    release_request.status = DefectReleaseRequestStatus.COMPLETED
    release_request.updated_by = user

    release_request.save(
        update_fields=[
            "status",
            "updated_by",
            "updated_at",
        ]
    )


# _apply_validation_decision_to_defect
# Met à jour le défaut selon la décision de validation.
def _apply_validation_decision_to_defect(
    *,
    defect,
    decision: str,
    user,
) -> None:
    """
    Applique au défaut le statut correspondant à la décision finale.
    """
    if decision == ValidationDecision.APPROVED:
        defect.status = DefectStatus.RELEASED
    else:
        defect.status = DefectStatus.OPEN

    defect.updated_by = user

    defect.save(
        update_fields=[
            "status",
            "updated_by",
            "updated_at",
        ]
    )



# _create_defect_release_validation
# Crée la décision finale liée à une demande de levée.
def _create_defect_release_validation(
    *,
    release_request,
    decision: str,
    validated_by,
    comment: str | None,
) -> DefectReleaseValidation:
    """
    Crée et retourne la validation associée à la demande de levée.
    """
    return DefectReleaseValidation.objects.create(
        release_request=release_request,
        decision=decision,
        validated_by=validated_by,
        comment=comment.strip() if comment else None,
        created_by=validated_by,
        updated_by=validated_by,
    )


# validate_defect_release_request
# Enregistre une décision finale sur une demande de levée.
@transaction.atomic
def validate_defect_release_request(
    *,
    release_request,
    decision: str,
    validated_by,
    comment: str | None = None,
) -> DefectReleaseValidation:
    """
    Valide une demande de levée et met à jour son défaut associé.
    """
    release_request = (
        DefectReleaseRequest.objects
        .select_for_update()
        .select_related("defect")
        .get(pk=release_request.pk)
    )

    _ensure_can_validate_defect_release_request(
        release_request=release_request,
        decision=decision,
        comment=comment,
    )

    validation = _create_defect_release_validation(
        release_request=release_request,
        decision=decision,
        validated_by=validated_by,
        comment=comment,
    )

    _mark_release_request_as_completed(
        release_request=release_request,
        user=validated_by,
    )

    _apply_validation_decision_to_defect(
        defect=release_request.defect,
        decision=decision,
        user=validated_by,
    )

    return validation
