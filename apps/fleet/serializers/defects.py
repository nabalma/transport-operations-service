
from rest_framework import serializers
from apps.fleet.models import Defect,CorrectiveAction,DefectReleaseValidation


# -- DefectSummary
class DefectSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Defect
        fields = (
            "id",
            "creation_source",
            "description",
            "status",
            "detected_at",
        )


# -- CorrectiveActionSummary
class CorrectiveActionSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrectiveAction
        fields = [         
            "description",
            "status",
            "evidence_url",
        ]



# -- DefectReleaseValidationSummary
class DefectReleaseValidationSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DefectReleaseValidation
        fields = [
            "id",
            "decision",
            "validated_by",
        ]





# -- Defect
class DefectSerializer(serializers.ModelSerializer):
    corrective_actions = CorrectiveActionSummarySerializer(
        many=True,
        read_only=True,
    )

    release_validations = DefectReleaseValidationSummarySerializer(
        many=True,
        read_only=True,
    )
    class Meta:
        model = Defect
        fields = "__all__"

        read_only_fields = [
            "id",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "is_deleted",
            "deleted_at",
            "deleted_by",
        ]


# -- CorrectiveAction
class CorrectiveActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrectiveAction
        fields = "__all__"

        read_only_fields = [
            "id",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "is_deleted",
            "deleted_at",
            "deleted_by",
        ]

# -- DefectReleaseValidation
class DefectReleaseValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefectReleaseValidation
        fields = "__all__"

        read_only_fields = [
            "id",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "is_deleted",
            "deleted_at",
            "deleted_by",
        ]

