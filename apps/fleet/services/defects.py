
from rest_framework.exceptions import ValidationError


# _build_defect_description
# Construit la description d’un défaut généré depuis un résultat d’inspection.
# Utilise le titre de la section, la référence du critère et le commentaire.
from apps.fleet.constants import DefectCreationSource, InspectionCriterionResultValue
from apps.fleet.models import Defect


def _build_defect_description(*, criterion_result):
    """
    Return the description of a defect generated from an inspection result.
    """
    criterion = criterion_result.criterion
    section = criterion.section
    comment = (criterion_result.comment or "").strip()

    description_prefix = (
        f"{section.title} - Ref. {criterion.reference}"
    )

    if comment:
        return f"{description_prefix} : {comment}"

    return (
        f"{description_prefix} : "
        "Critère en défaut relevé lors de l’inspection."
    )


# _ensure_can_create_defect_from_failed_criterion_result
# Validate that a criterion result can generate a defect.
def _ensure_can_create_defect_from_failed_criterion_result(
    *,
    criterion_result,
):
    """
    Validate that the criterion result can generate a defect.
    """
    if criterion_result.result != InspectionCriterionResultValue.FAIL:
        raise ValidationError(
            {
                "result": (
                    "Only a failed criterion result can generate a defect."
                )
            }
        )

    if not criterion_result.criterion.creates_defect_if_failed:
        raise ValidationError(
            {
                "criterion": (
                    "This criterion is not configured to generate a defect."
                )
            }
        )




# create_defect_from_failed_criterion_result
# Crée un défaut depuis un résultat de critère en échec.
# Le résultat doit provenir d’un critère configuré pour générer un défaut.
def create_defect_from_failed_criterion_result(
    *,
    criterion_result,
    user
):
    """
    Create and return a system-generated defect from a failed criterion result.
    """
    _ensure_can_create_defect_from_failed_criterion_result(
        criterion_result=criterion_result,
    )

    criterion = criterion_result.criterion
    inspection = criterion_result.inspection

    defect = Defect.objects.create(
        vehicle=inspection.vehicle,
        creation_source=DefectCreationSource.SYSTEM,
        source_inspection=inspection,
        source_inspection_criterion_result=criterion_result,
        description=_build_defect_description(criterion_result=criterion_result,),
        created_by=user,
        updated_by=user,
    )

    return defect
