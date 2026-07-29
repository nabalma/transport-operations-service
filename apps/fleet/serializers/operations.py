from rest_framework import serializers

from apps.fleet.models import (
    Downtime,
    ReturnToService,
)



class DowntimeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Downtime
        fields = [
            "source_type",
            "status",
        ]


class ReturnToServiceSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnToService
        fields = [
            "source_type",
            "proposed_by_system",
            "decision",
        ]



class DowntimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Downtime
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