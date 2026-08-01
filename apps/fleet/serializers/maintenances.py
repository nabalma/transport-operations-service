
from apps.fleet.models import MaintenanceWorkOrder,MaintenanceSchedule, MaintenanceComponent,MaintenanceWorkOrderItem,MaintenancePolicy
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

    def validate(self, attrs: dict) -> dict:
        """
        Empêche le déplacement d'une intervention vers un autre
        ordre de travail après sa création.
        """

        if self.instance is None:
            return attrs

        work_order = attrs.get("work_order")

        if (
            work_order is not None
            and work_order != self.instance.work_order
        ):
            raise serializers.ValidationError(
                {
                    "work_order": (
                        "Une intervention ne peut pas être déplacée "
                        "vers un autre ordre de travail."
                    )
                }
            )

        return attrs

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



class MaintenanceWorkOrderSerializer(serializers.ModelSerializer):
    """
    Serializer des ordres de travail de maintenance.

    La création et les modifications métier sont déléguées
    aux services de maintenance.
    """

    items = MaintenanceWorkOrderItemSerializer(
        many=True,
        read_only=True,
    )



    def validate(self, attrs):
        if self.instance is None:
            return attrs

        vehicle = attrs.get("vehicle")

        if vehicle is not None and vehicle != self.instance.vehicle:
            raise serializers.ValidationError(
                {
                    "vehicle": (
                        "Le véhicule d’un ordre de travail ne peut pas "
                        "être modifié après sa création."
                    )
                }
            )

        return attrs



    class Meta:
        model = MaintenanceWorkOrder

        fields = (
            "id",
            "vehicle",
            "kind",
            "status",
            "title",
            "description",
            "schedule",
            "defect",
            "planned_start_at",
            "planned_end_at",
            "completed_at",
            "cancelled_at",
            "completion_notes",
            "cancellation_reason",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
              "items",
        )

        read_only_fields = (
            "id",
            "status",
            "completed_at",
            "cancelled_at",
            "completion_notes",
            "cancellation_reason",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )



class MaintenanceWorkOrderCompleteInputSerializer(
    serializers.Serializer,
):
    """
    Valide les données nécessaires à la clôture d’un ordre de travail.
    """

    completion_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        trim_whitespace=True,
    )



class MaintenanceWorkOrderCancelInputSerializer(
    serializers.Serializer,
):
    """
    Valide les données nécessaires à l’annulation d’un ordre de travail.
    """

    cancellation_reason = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )


class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer des planifications de maintenance préventive.
    """

    def validate(self, attrs):
            """
            Empêche de modifier le véhicule ou la politique
            après la création de la planification.
            """

            if self.instance is None:
                return attrs

            vehicle = attrs.get("vehicle")
            policy = attrs.get("policy")

            if (
                vehicle is not None
                and vehicle != self.instance.vehicle
            ):
                raise serializers.ValidationError(
                    {
                        "vehicle": (
                            "Le véhicule d’une planification ne peut pas "
                            "être modifié."
                        )
                    }
                )

            if (
                policy is not None
                and policy != self.instance.policy
            ):
                raise serializers.ValidationError(
                    {
                        "policy": (
                            "La politique d’une planification ne peut pas "
                            "être modifiée."
                        )
                    }
                )

            return attrs

    class Meta:
        model = MaintenanceSchedule

        fields = (
            "id",
            "vehicle",
            "policy",
            "status",
            "due_at",
            "due_mileage",
            "due_engine_hours",
            "fulfilled_at",
            "cancelled_at",
            "cancellation_reason",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )

        read_only_fields = (
            "id",
            "status",
            "fulfilled_at",
            "cancelled_at",
            "cancellation_reason",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )


class MaintenanceScheduleCancelInputSerializer(
    serializers.Serializer,
):
    """
    Valide les données nécessaires à l’annulation
    d’une planification de maintenance.
    """

    cancellation_reason = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )
    