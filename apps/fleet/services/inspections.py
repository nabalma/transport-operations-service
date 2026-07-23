from datetime import date
from decimal import Decimal

from apps.fleet.constants import InspectionContext, InspectionCriterionResultValue, InspectionOverallResult, InspectionScoringPolicyStatus, InspectionStatus
from apps.fleet.services.defects import create_defect_from_failed_criterion_result
from apps.fleet.services.membership import _ensure_vehicle_has_active_membership, get_active_vehicle_membership
from apps.fleet.services.vehicles import _ensure_vehicle_is_active, _get_valid_carrier_or_error
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Prefetch, QuerySet
from django.utils import timezone

from apps.fleet.models import Inspection, InspectionChapter, InspectionCriterionResult, InspectionScoringPolicyConfiguration, InspectionVersion, InspectionCriterion, InspectionSection, Vehicle


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


# build_inspection_chapters
# Construit les chapitres liés à la version d’inspection sélectionnée.
# Chaque chapitre contient uniquement ses sections actives.
def build_inspection_chapters(*,inspection_version: InspectionVersion,) -> list[dict]:
    """
    Construit les chapitres de la fiche d'inspection vierge.

    Les chapitres supprimés ou inactifs sont exclus du résultat.
    """

    chapters = inspection_version.chapters.all()

    return [
        {
            "reference": chapter.reference,
            "title": chapter.title,
            "sections": build_inspection_sections(
                chapter=chapter,
            ),
        }
        for chapter in chapters
    ]



# build_inspection_sections
# Construit les sections liées à un chapitre d’inspection.
# Chaque section contient uniquement ses critères actifs.
def build_inspection_sections(*,chapter: InspectionChapter,) -> list[dict]:
    """
    Construit les sections actives d’un chapitre d’inspection.
    Les sections supprimées ou inactives sont exclues du résultat.
    """

    sections = chapter.sections.all()

    return [
        {
            "reference": section.reference,
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

    criteria = section.criteria.all()

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
    courante et la construction de l’en-tête et les chapitres.
    """

    _validate_inspection_context(inspection_context=inspection_context,)

    inspection_version = _get_current_inspection_version(inspection_context=inspection_context,)
    inspection_version = get_inspection_version_tree(inspection_version=inspection_version,)

    header = build_inspection_header(
        vehicle=vehicle,
        inspection_date=inspection_date,
        location_name=location_name,
        driver_name=driver_name,
        inspector_name=inspector_name,
    )
    chapters = build_inspection_chapters(inspection_version=inspection_version,)

    return {
        "inspection_version": str(inspection_version.id),
        "inspection_context": inspection_version.context,
        "version": inspection_version.version,
        "header": header,
        "chapters": chapters,
        
       
    }

# =======================================
# CREER UNE INSPECTION DUN VEHICULE
# =======================================


# _ensure_vehicle_has_no_in_progress_inspection
# Ensures that the vehicle has no inspection currently in progress.
def _ensure_vehicle_has_no_in_progress_inspection(*, vehicle):
    """
    Validate that the vehicle has no active inspection in progress.
    """
    has_in_progress_inspection = Inspection.objects.filter(
        vehicle=vehicle,
        status=InspectionStatus.IN_PROGRESS,
        is_deleted=False,
    ).exists()

    if has_in_progress_inspection:
        raise ValidationError(
            {
                "vehicle": (
                    "This vehicle already has an inspection in progress."
                )
            }
        )


# create_inspection
# Creates a new inspection for a vehicle.
# Resolves the applicable inspection version automatically.
@transaction.atomic
def create_inspection(*,vehicle : Vehicle, inspection_context: str, inspector,)-> Inspection :
    """
    Create a new inspection using the current version
    for the requested inspection context.
    """

    _validate_inspection_context(inspection_context=inspection_context,)
    inspection_version = _get_current_inspection_version(inspection_context=inspection_context,)
    _ensure_vehicle_has_active_membership(vehicle=vehicle,)
    _get_valid_carrier_or_error(vehicle=vehicle,)
    _ensure_vehicle_is_active(vehicle=vehicle,)
    _ensure_vehicle_has_no_in_progress_inspection(vehicle=vehicle,)

    inspection = Inspection.objects.create(
        vehicle=vehicle,
        inspection_version=inspection_version,
        inspection_date=timezone.now(),
        inspector=inspector,
        status=InspectionStatus.IN_PROGRESS,
        created_by=inspector,
        updated_by=inspector,)

    return inspection

# =======================================
# CANCELLER UNE INSPECTION DUN VEHICULE
# =======================================

# cancel_inspection
# Cancels an inspection currently in progress.
# Only an active inspection with status IN_PROGRESS can be cancelled.
@transaction.atomic
def cancel_inspection(*,inspection: Inspection,user,) -> Inspection:
    """
    Cancel an inspection and record the user who performed the action.
    """
    if inspection.is_deleted:
        raise ValidationError(
            {
                "inspection": (
                    "A deleted inspection cannot be cancelled."
                )
            }
        )

    if inspection.status != InspectionStatus.IN_PROGRESS:
        raise ValidationError(
            {
                "status": (
                    "Only an inspection in progress can be cancelled."
                )
            }
        )

    inspection.status = InspectionStatus.CANCELLED
    inspection.updated_by = user
    inspection.save(
        update_fields=[
            "status",
            "updated_by",
            "updated_at",
        ]
    )

    return inspection



# =======================================================
# ENREGISTRER UNE REPONSE A  UNE INSPECTION DUN VEHICULE
# =======================================================

# record_criterion_result
# Records the result of one criterion for an inspection.
# Only an active inspection in progress can receive a criterion result.
@transaction.atomic
def record_criterion_result(*,inspection: Inspection,criterion: InspectionCriterion,result: str, user, comment: str | None = None,) -> InspectionCriterionResult:
    """
    Create a result for one criterion of an inspection in progress.
    """
    if inspection.is_deleted:
        raise ValidationError(
            {
                "inspection": (
                    "A deleted inspection cannot receive criterion results."
                )
            }
        )

    if inspection.status != InspectionStatus.IN_PROGRESS:
        raise ValidationError(
            {
                "inspection": (
                    "Only an inspection in progress can receive "
                    "criterion results."
                )
            }
        )

    has_active_result = InspectionCriterionResult.objects.filter(
        inspection=inspection,
        criterion=criterion,
        is_deleted=False,
    ).exists()

    if has_active_result:
        raise ValidationError(
            {
                "criterion": (
                    "This criterion already has an active result "
                    "for this inspection."
                )
            }
        )

    criterion_result = InspectionCriterionResult(
        inspection=inspection,
        criterion=criterion,
        result=result,
        comment=comment or "",
        created_by=user,
        updated_by=user,
    )

    try:
        criterion_result.full_clean()
    except DjangoValidationError as exc:
        raise ValidationError(exc.message_dict) from exc

    criterion_result.save()

    if (
    criterion_result.result == InspectionCriterionResultValue.FAIL and criterion_result.criterion.creates_defect_if_failed ):
        create_defect_from_failed_criterion_result(criterion_result=criterion_result,)

    return criterion_result



# _get_inspection_criterion_or_error
# Retrieves an active inspection criterion by its identifier.
def _get_inspection_criterion_or_error(*,criterion_id,) -> InspectionCriterion:
    """
    Return an active inspection criterion.
    """
    criterion = InspectionCriterion.objects.filter(
        id=criterion_id,
        is_deleted=False,
        is_active=True,
    ).first()

    if criterion is None:
        raise ValidationError(
            {
                "criterion_id": (
                    "No active inspection criterion was found "
                    "with this identifier."
                )
            }
        )

    return criterion
 


# _get_active_criteria_prefetch
# Build the prefetch used to load active inspection criteria.
def _get_active_criteria_prefetch() -> Prefetch:
    """
    Return the Prefetch object for active inspection criteria.
    """
    return Prefetch(
        "criteria",
        queryset=InspectionCriterion.objects.filter(
            is_deleted=False,
            is_active=True,
        ).order_by(
            "position",
        ),
    )

# _get_active_sections_prefetch
# Build the prefetch used to load active inspection sections.
# Each section also loads its active criteria.
def _get_active_sections_prefetch() -> Prefetch:
    """
    Return the Prefetch object for active inspection sections.
    """
    return Prefetch(
        "sections",
        queryset=(
            InspectionSection.objects
            .filter(
                is_deleted=False,
                is_active=True,
            )
            .prefetch_related(
                _get_active_criteria_prefetch(),
            )
            .order_by(
                "position",
            )
        ),
    )

# _get_active_chapters_prefetch
# Build the prefetch used to load active inspection chapters.
# Each chapter also loads its active sections and criteria.
def _get_active_chapters_prefetch() -> Prefetch:
    """
    Return the Prefetch object for active inspection chapters.
    """
    return Prefetch(
        "chapters",
        queryset=(
            InspectionChapter.objects
            .filter(
                is_deleted=False,
                is_active=True,
            )
            .prefetch_related(
                _get_active_sections_prefetch(),
            )
            .order_by(
                "position",
            )
        ),
    )


# get_inspection_version_tree
# Return one inspection version with its active configuration tree.
# Active chapters, sections, and criteria are prefetched.
def get_inspection_version_tree(
    *,
    inspection_version: InspectionVersion,
) -> InspectionVersion:
    """
    Return the inspection version with its active tree loaded.
    """
    return (
        InspectionVersion.objects
        .prefetch_related(
            _get_active_chapters_prefetch(),
        )
        .get(
            id=inspection_version.id,
            is_deleted=False,
        )
    )



# get_expected_inspection_criteria
# Returns all active criteria expected for an inspection.
def get_expected_inspection_criteria(*,inspection: Inspection,) -> QuerySet[InspectionCriterion]:
    """
    Return active criteria belonging to the inspection version.
    """
    return InspectionCriterion.objects.filter(
        section__chapter__inspection_version=inspection.inspection_version,
        is_deleted=False,
        is_active=True,
        section__is_deleted=False,
        section__is_active=True,
        section__chapter__is_deleted=False,
        section__chapter__is_active=True,
    )

# get_recorded_criterion_results_count
# Returns the number of active criterion results recorded for an inspection.
def get_recorded_criterion_results_count(*,inspection: Inspection,) -> int:
    """
    Return the number of active criterion results for an inspection.
    """
    return InspectionCriterionResult.objects.filter(
        inspection=inspection,
        is_deleted=False,
    ).count()


# _ensure_all_expected_criteria_are_recorded
# Ensures that every expected criterion has an active recorded result.
def _ensure_all_expected_criteria_are_recorded(*,inspection: Inspection,) -> None:
    """
    Validate that all expected criteria have been recorded.
    """
    expected_count = get_expected_inspection_criteria(inspection=inspection,).count()
    recorded_count = get_recorded_criterion_results_count(inspection=inspection,)

    if expected_count != recorded_count:
        raise ValidationError(
            {
                "inspection": (
                    "All expected criteria must be recorded "
                    "before completing the inspection."
                )
            }
        )
    

# calculate_inspection_overall_result
# Calculates the overall result from active criterion results.
# A failed blocking criterion always forces a FAIL result.
def calculate_inspection_overall_result(*,inspection: Inspection,) -> str:
    """
    Calculate the overall result of an inspection.
    """
    membership = get_active_vehicle_membership(vehicle=inspection.vehicle,)
    scoring_policy = get_active_inspection_scoring_policy(membership_type=membership.membership_type,context=inspection.context,)


    criterion_results = (
        InspectionCriterionResult.objects
        .filter(
            inspection=inspection,
            is_deleted=False,
        )
        .select_related(
            "criterion",
        )
    )

    has_blocking_failure = criterion_results.filter(
        result=InspectionCriterionResultValue.FAIL,
        criterion__is_blocking_if_failed=True,
    ).exists()

    if has_blocking_failure:
        return InspectionOverallResult.FAIL

    applicable_results = criterion_results.exclude(result=InspectionCriterionResultValue.NOT_APPLICABLE,)
    possible_points = applicable_results.count()
    earned_points = applicable_results.filter(result=InspectionCriterionResultValue.PASS,).count()

    if possible_points == 0:
        raise ValidationError(
            {
                "overall_result": (
                    "The inspection score cannot be calculated because "
                    "there are no applicable criterion results."
                ),
            },
    )

    score_percentage = (Decimal(earned_points)/ Decimal(possible_points)* Decimal("100"))

    if score_percentage >= scoring_policy.pass_threshold:
        return InspectionOverallResult.PASS

    if score_percentage >= scoring_policy.pass_threshold:
        return InspectionOverallResult.PASS_WITH_OBSERVATION

    return InspectionOverallResult.FAIL



# complete_inspection
# Completes an inspection after validating business rules.
@transaction.atomic
def complete_inspection(*,inspection: Inspection,user,) -> Inspection:
    """
    Complete an inspection.
    """
    if inspection.is_deleted:
        raise ValidationError(
            {
                "inspection": (
                    "A deleted inspection cannot be completed."
                )
            }
        )

    if inspection.status != InspectionStatus.IN_PROGRESS:
        raise ValidationError(
            {
                "inspection": (
                    "Only an inspection in progress can be completed."
                )
            }
        )
    _ensure_all_expected_criteria_are_recorded(inspection=inspection,)
    overall_result = calculate_inspection_overall_result(inspection=inspection,)
    inspection.overall_result = overall_result
    inspection.status = InspectionStatus.COMPLETED
    inspection.updated_by = user

    inspection.save(
    update_fields=[
        "overall_result",
        "status",
        "updated_by",
        "updated_at",
    ])

    return inspection


# get_active_inspection_scoring_policy
# Returns the active scoring policy for a membership type and context.
def get_active_inspection_scoring_policy(*,membership_type: str,context: str,) -> InspectionScoringPolicyConfiguration:
    """
    Return the active and non-deleted scoring policy configuration.
    """
    try:
        return InspectionScoringPolicyConfiguration.objects.get(
            membership_type=membership_type,
            context=context,
            status=InspectionScoringPolicyStatus.ACTIVE,
            is_deleted=False,
        )
    except InspectionScoringPolicyConfiguration.DoesNotExist as exc:
        raise ValidationError(
            {
                "scoring_policy": (
                    "No active scoring policy configuration was found."
                ),
            },
        ) from exc
    
# _get_scoring_policy_for_activation
# Returns the scoring policy to activate.
def _get_scoring_policy_for_activation(*,policy_id,) -> InspectionScoringPolicyConfiguration:
    """
    Return the non-deleted scoring policy locked for update.
    """
    try:
        return (
            InspectionScoringPolicyConfiguration.objects
            .select_for_update()
            .get(
                pk=policy_id,
                is_deleted=False,
            )
        )
    except InspectionScoringPolicyConfiguration.DoesNotExist as exc:
        raise ValidationError(
            {
                "scoring_policy": (
                    "The scoring policy does not exist or has been deleted."
                ),
            },
        ) from exc
    

# _ensure_scoring_policy_can_be_activated
# Ensures that only a draft scoring policy can be activated.
def _ensure_scoring_policy_can_be_activated(*,policy: InspectionScoringPolicyConfiguration,) -> None:
    """
    Validate that the scoring policy can transition to ACTIVE.
    """
    if policy.status != InspectionScoringPolicyStatus.DRAFT:
        raise ValidationError(
            {
                "status": (
                    "Only a draft scoring policy can be activated."
                ),
            },
        )
    

# _retire_active_scoring_policy
# Retires the active policy for a membership type and inspection context.
def _retire_active_scoring_policy(*,membership_type: str,context: str,user,retired_at,) -> None:
    """
    Retire the current active scoring policy when one exists.
    """
    current_policy = (
        InspectionScoringPolicyConfiguration.objects
        .select_for_update()
        .filter(
            membership_type=membership_type,
            context=context,
            status=InspectionScoringPolicyStatus.ACTIVE,
            is_deleted=False,
        )
        .first()
    )

    if current_policy is None:
        return

    current_policy.status = InspectionScoringPolicyStatus.RETIRED
    current_policy.retired_at = retired_at
    current_policy.updated_by = user

    current_policy.save(
        update_fields=[
            "status",
            "retired_at",
            "updated_by",
            "updated_at",
        ],
    )
    

# _activate_scoring_policy
# Activates the selected scoring policy.
def _activate_scoring_policy(*,policy: InspectionScoringPolicyConfiguration,user,activated_at,) -> InspectionScoringPolicyConfiguration:
    """
    Activate the selected scoring policy.
    """
    policy.status = InspectionScoringPolicyStatus.ACTIVE
    policy.activated_at = activated_at
    policy.retired_at = None
    policy.updated_by = user

    policy.save(
        update_fields=[
            "status",
            "activated_at",
            "retired_at",
            "updated_by",
            "updated_at",
        ],
    )

    return policy


# activate_inspection_scoring_policy
# Activates an inspection scoring policy.
# activate_inspection_scoring_policy
# Activates an inspection scoring policy.
@transaction.atomic
def activate_inspection_scoring_policy(*,policy: InspectionScoringPolicyConfiguration,user,) -> InspectionScoringPolicyConfiguration:
    """
    Activate an inspection scoring policy.
    """
    policy = _get_scoring_policy_for_activation(policy_id=policy.pk,)
    _ensure_scoring_policy_can_be_activated(policy=policy,)
    activation_date = timezone.now()
    _retire_active_scoring_policy(membership_type=policy.membership_type,context=policy.context,user=user,retired_at=activation_date,)
    return _activate_scoring_policy(policy=policy,user=user,activated_at=activation_date,)