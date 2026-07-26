from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError

from apps.fleet.constants import (DefectCreationSource,)
from apps.fleet.models import Defect



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

