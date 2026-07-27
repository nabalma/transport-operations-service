
from rest_framework import serializers
from apps.fleet.models import Defect,DefectReleaseValidation,DefectReleaseRequest


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

# DefectReleaseRequestSubmitSerializer
# Valide les données nécessaires à la soumission d’une demande de levée.
class DefectReleaseRequestSubmitSerializer(serializers.Serializer):
    """
    Représente les données fournies par le client lors d’une soumission.
    """

    correction_summary = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )


# DefectReleaseRequestSerializer
# Sérialise une demande de levée de défaut.
class DefectReleaseRequestSerializer(serializers.ModelSerializer):
    """
    Représente une demande de levée de défaut dans les réponses API.
    """

    class Meta:
        model = DefectReleaseRequest
        fields = (
            "id",
            "defect",
            "correction_summary",
            "submitted_by",
            "submitted_at",
            "status",
        )
        read_only_fields = fields



from apps.fleet.constants import ValidationDecision


# DefectReleaseValidationInputSerializer
# Valide les données nécessaires à la décision finale.
class DefectReleaseValidationInputSerializer(serializers.Serializer):
    """
    Représente les données reçues pour valider une demande de levée.
    """

    decision = serializers.ChoiceField(
        choices=ValidationDecision.choices,
    )
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        trim_whitespace=True,
    )

