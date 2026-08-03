from apps.fleet.constants import ReturnToServiceSourceType
from apps.fleet.models.operations import Downtime, DowntimeCause, ReturnToService
from apps.fleet.models.vehicles import Vehicle
from rest_framework import serializers


class DowntimeCauseSerializer(serializers.ModelSerializer):
    """
    Sérialise une cause liée à une immobilisation.
    """

    class Meta:
        model = DowntimeCause

        fields = (
            "id",
            "inspection_criterion_result",
            "defect",
            "reason",
            "is_resolved",
            "resolved_at",
            "resolved_by",
            "created_at",
            "created_by",
        )

        read_only_fields = fields


class DowntimeSerializer(serializers.ModelSerializer):
    """
    Sérialise une immobilisation avec ses causes actives.
    """

    causes = DowntimeCauseSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Downtime

        fields = (
            "id",
            "vehicle",
            "status",
            "start_date",
            "end_date",
            "causes",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )

        read_only_fields = fields




class DowntimeCreateInputSerializer(serializers.Serializer):
    """
    Valide les données nécessaires à une immobilisation manuelle.
    """

    vehicle = serializers.PrimaryKeyRelatedField(
        queryset=Vehicle.objects.filter(
            is_deleted=False,
        ),
    )

    reason = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )

    start_date = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )




class ReturnToServiceSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnToService
        fields = [
            "source_type",
            "proposed_by_system",
            "decision",
        ]

class ReturnToServiceCreateInputSerializer(
    serializers.Serializer,
):
    source_type = serializers.ChoiceField(
        choices=ReturnToServiceSourceType.choices,
    )

    source_id = serializers.UUIDField(
        required=False,
        allow_null=True,
    )

    proposed_by_system = serializers.BooleanField(
        default=False,
    )





class ReturnToServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnToService
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


class ReturnToServiceApproveInputSerializer(
    serializers.Serializer,
):
    """
    Valide les données facultatives d’une approbation.
    """

    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        trim_whitespace=True,
    )


class ReturnToServiceRejectInputSerializer(
    serializers.Serializer,
):
    """
    Valide les données nécessaires au rejet.
    """

    comment = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )