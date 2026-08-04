from rest_framework import serializers
from apps.trips.models.models import NextTripEligibilityEvaluation, NextTripEligibilityEvaluationReason





class NextTripEligibilityEvaluationReasonSummarySerializer(
    serializers.ModelSerializer,
):
    """
    Sérialise une raison résumée d’inéligibilité
    au prochain voyage.
    """

    class Meta:
        model = NextTripEligibilityEvaluationReason

        fields = (
            "reason_type",
            "message",
            "source_id",
        )

        read_only_fields = fields



class NextTripEligibilityEvaluationSerializer(
    serializers.ModelSerializer
):
    evaluation_reasons = (
        NextTripEligibilityEvaluationReasonSummarySerializer(
            many=True,
            read_only=True,
        )
    )

    class Meta:
        model = NextTripEligibilityEvaluation
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


class NextTripEligibilityEvaluationReasonSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = NextTripEligibilityEvaluationReason
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
