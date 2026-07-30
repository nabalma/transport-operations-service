
from apps.fleet.models import MaintenanceComponent,MaintenanceWorkOrderItem,MaintenancePolicy
from rest_framework import serializers

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
            "id",
            "created_by",
            "updated_by",
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "deleted_reason",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "deleted_reason",
        ]


class MaintenanceComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceComponent
        fields = [
            "id",
            "code",
            "name",
            "scope",
            "description",
            "is_active",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "deleted_reason",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "deleted_reason",
        ]



class MaintenanceWorkOrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer d’une intervention appartenant à un ordre de travail.
    """

    component_name = serializers.CharField(
        source="component.name",
        read_only=True,
    )

    component_scope = serializers.CharField(
        source="component.scope",
        read_only=True,
    )

    class Meta:
        model = MaintenanceWorkOrderItem

        fields = (
            "id",
            "work_order",
            "component",
            "component_name",
            "component_scope",
            "description",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )

        read_only_fields = (
            "id",
            "component_name",
            "component_scope",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )