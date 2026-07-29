
from rest_framework import serializers

from apps.fleet.models import MaintenancePolicy

class MaintenancePolicySerializer(serializers.ModelSerializer):
    """
    Sérialise les politiques de maintenance.
    """

    class Meta:
        model = MaintenancePolicy
        fields = [
            "id",
            "code",
            "name",
            "description",
            "interval_days",
            "interval_mileage",
            "interval_engine_hours",
            "tolerance_days",
            "tolerance_mileage",
            "tolerance_engine_hours",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]