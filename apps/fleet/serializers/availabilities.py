from rest_framework import serializers

from apps.fleet.models import (
    NextTripEligibilityEvaluation,
    NextTripEligibilityEvaluationReason,
    VehicleAvailabilityEvaluation,
    VehicleAvailabilityEvaluationReason,
)


class VehicleAvailabilityEvaluationSummarySerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = VehicleAvailabilityEvaluation
        fields = [
            "id",
            "calculated_result",
            "final_result",
        ]


class VehicleAvailabilityEvaluationReasonSummarySerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = VehicleAvailabilityEvaluationReason
        fields = [
            "reason_type",
            "message",
            "source_id",
        ]


class NextTripEligibilityEvaluationSummarySerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = NextTripEligibilityEvaluation
        fields = [
            "id",
            "evaluated_at",
            "result",
            "rule_version",
        ]


class NextTripEligibilityEvaluationReasonSummarySerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = NextTripEligibilityEvaluationReason
        fields = [
            "id",
            "reason_type",
            "message",
            "source_id",
        ]


class VehicleAvailabilityEvaluationSerializer(
    serializers.ModelSerializer
):
    evaluation_reasons = (
        VehicleAvailabilityEvaluationReasonSummarySerializer(
            many=True,
            read_only=True,
        )
    )

    class Meta:
        model = VehicleAvailabilityEvaluation
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


class VehicleAvailabilityEvaluationReasonSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = VehicleAvailabilityEvaluationReason
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