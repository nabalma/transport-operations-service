
from apps.fleet.constants import InspectionContext, InspectionCriterionResultValue, InspectionLocationType
from rest_framework import serializers
from apps.fleet.models import InspectionSection,InspectionCriterion,InspectionCriterionResult,InspectionScoringPolicyConfiguration,InspectionVersion,Inspection,Vehicle,InspectionChapter
from .defects import DefectSummarySerializer




# =============================================================================
# InspectionSectionSummarySerializer
#
# Représentation légère d’une section dans les réponses imbriquées.
# =============================================================================
class InspectionSectionSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionSection
        fields = (
            "id",
            "reference",
            "code",
            "title",
            "is_active",
        )


# =============================================================================
# InspectionCriterionSummarySerializer
#
# Représentation légère d’un critère appartenant à une section versionnée.
# =============================================================================
class InspectionCriterionSummarySerializer(serializers.ModelSerializer):
    section = InspectionSectionSummarySerializer(
        read_only=True,
    )

    class Meta:
        model = InspectionCriterion
        fields = (
            "id",
            "section",
            "reference",
            "code",
            "label",
            "creates_defect_if_failed",
            "is_blocking_if_failed",
            "is_active",
        )




# =============================================================================
# InspectionCriterionResultSummarySerializer
#
# Représentation légère du résultat d’un critère dans une inspection.
#
# Le résultat pointe directement vers InspectionCriterion.
# =============================================================================
class InspectionCriterionResultSummarySerializer(
    serializers.ModelSerializer
):
    criterion = InspectionCriterionSummarySerializer(read_only=True,)
    defect = DefectSummarySerializer(read_only=True,)


    class Meta:
        model = InspectionCriterionResult
        fields = (
            "id",
            "criterion",
            "result",
            "comment",
            "defect"
            
        )


# -- InspectionScoringPolicyConfiguration
class InspectionScoringPolicyConfigurationSerializer(serializers.ModelSerializer,):
    class Meta:
        model = InspectionScoringPolicyConfiguration
        fields = "__all__"

        read_only_fields = [
            "id",
            "activated_at",
            "retired_at",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "is_deleted",
            "deleted_at",
            "deleted_by",
        ]


# =============================================================================
# InspectionContextVersionSerializer
#
# Gère une version complète d’un formulaire d’inspection.
#
# Après création, les champs context, version et source_version sont
# immuables. Seul is_current peut être modifié.
# =============================================================================
class InspectionVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionVersion
        fields = (
            "id",
            "context",
            "version",
            "source_version",
            "is_current",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )

        read_only_fields = (
            "id",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )

    def validate(self, attrs):
        if self.instance is None:
            return attrs

        immutable_fields = (
            "context",
            "version",
            "source_version",
        )

        modified_fields = [
            field
            for field in immutable_fields
            if field in attrs
            and attrs[field] != getattr(self.instance, field)
        ]

        if modified_fields:
            raise serializers.ValidationError(
                {
                    field: "Ce champ ne peut pas être modifié."
                    for field in modified_fields
                }
            )

        return attrs


# InspectionChapterSerializer
# Sérialise les chapitres d’une version d’inspection.
# Expose les champs nécessaires à leur gestion via l’API.
class InspectionChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionChapter
        fields = (
            "id",
            "position",
            "inspection_version",
            "reference",
            "code",
            "title",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


# =============================================================================
# InspectionSectionSerializer
#
# Gère les sections appartenant directement à une version d’inspection.
# =============================================================================
class InspectionSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionSection
        fields = (
            "id",
            "position",
            "chapter",
            "reference",
            "code",
            "title",
            "is_active",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )

        read_only_fields = (
            "id",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )


# =============================================================================
# InspectionCriterionSerializer
#
# Gère les critères appartenant directement à une section versionnée.
# =============================================================================
class InspectionCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionCriterion
        fields = (
            "id",
            "section",
            "reference",
            "position",
            "code",
            "label",
            "creates_defect_if_failed",
            "is_blocking_if_failed",
            "is_active",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )

        read_only_fields = (
            "id",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )

# RecordCriterionResultInputSerializer
# Validates the input required to record one criterion result.
class RecordCriterionResultInputSerializer(serializers.Serializer):
    criterion_id = serializers.UUIDField()

    result = serializers.ChoiceField(
        choices=InspectionCriterionResultValue.choices,
    )

    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )


# =============================================================================
# InspectionSerializer
#
# Gère une inspection réelle et expose les résultats des critères
# en lecture seule.
# =============================================================================
class InspectionSerializer(serializers.ModelSerializer):
    criterion_results = InspectionCriterionResultSummarySerializer(
        many=True,
        read_only=True,
    )

    context = serializers.CharField(
        source="inspection_version.context",
        read_only=True,
    )

    class Meta:
        model = Inspection
        fields = (
            "id",
            "vehicle",
            "inspection_version",
            "context",
            "inspection_date",
            "inspector",
            "status",
            "overall_result",
            "comments",
            "criterion_results",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            
        )

        read_only_fields = (
            "id",
            "context",
            "criterion_results",
         #   "status",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )


# CreateInspectionSerializer
# Validates the data required to start an inspection.
class CreateInspectionSerializer(serializers.Serializer):
    vehicle_id = serializers.UUIDField()
    inspection_context = serializers.CharField()





# =============================================================================
# InspectionCriterionResultSerializer
#
# Gère le résultat d’un critère pour une inspection.
#
# Vérifie que le critère appartient à la même version que l’inspection.
# =============================================================================
class InspectionCriterionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionCriterionResult
        fields = (
            "id",
            "inspection",
            "criterion",
            "result",
            "comment",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )

        read_only_fields = (
            "id",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )

    def validate(self, attrs):
        inspection = attrs.get(
            "inspection",
            getattr(self.instance, "inspection", None),
        )

        criterion = attrs.get(
            "criterion",
            getattr(self.instance, "criterion", None),
        )

        if inspection is None or criterion is None:
            return attrs

        criterion_version_id = (
            criterion.section.chapter.inspection_version_id
        )

        if criterion_version_id != inspection.inspection_version_id:
            raise serializers.ValidationError(
                {
                    "criterion": (
                        "Le critère n’appartient pas à la version "
                        "utilisée par cette inspection."
                    ),
                }
            )

        return attrs
    

# -------------------------------------------------------------------
# InspectionLocationInputSerializer
# Données décrivant le lieu où l'inspection est effectuée.
# -------------------------------------------------------------------
class InspectionLocationInputSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=InspectionLocationType.choices,)
    name = serializers.CharField(max_length=255,)



# -------------------------------------------------------------------
# GenerateInspectionSheetInputSerializer
# Données requises pour générer une fiche d’inspection vierge.
# -------------------------------------------------------------------
class GenerateInspectionSheetInputSerializer(serializers.Serializer):
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(),)
    inspection_type = serializers.ChoiceField(choices=InspectionContext.choices,)
    inspection_date = serializers.DateField()
    location = InspectionLocationInputSerializer()


