from rest_framework import serializers
from apps.fleet.models import VehicleAgePolicyConfiguration,Vehicle,TankerCompartment,VehicleMembership,VehicleDocument,VehicleMembershipRequest
from .carriers import CarrierSummarySerializer



#---VehicleSummary
class VehicleSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            "id",
            "display_registration",
            "status",
        ]

# -- TankerCompartmentSummary
class TankerCompartmentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TankerCompartment
        fields = [
            "compartment_number",
            "capacity_liters",
        ]

# -- VehicleMembershipSummary
class VehicleMembershipSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleMembership
        fields = [
            "membership_type",
            "status",
        ]


# -- VehicleDocumentSummary
class VehicleDocumentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleDocument
        fields = [
            "document_type",
            "expires_at",
        ]



# -- VehicleAgePolicyConfiguration
class VehicleAgePolicyConfigurationSerializer(serializers.ModelSerializer):

    class Meta:
        model = VehicleAgePolicyConfiguration
        fields = "__all__"
        read_only_fields = [
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]

# -- Vehicle 
class VehicleSerializer(serializers.ModelSerializer):
    tanker_compartments = TankerCompartmentSummarySerializer(many=True,read_only=True,)
    vehicle_memberships=VehicleMembershipSummarySerializer(many=True,read_only=True,)
    documents = VehicleDocumentSummarySerializer(many=True,read_only=True,)
    
    class Meta:
        model = Vehicle
        fields = "__all__"
        read_only_fields = [
            "id",
            "display_registration",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


# -- Compartiements 
class TankerCompartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TankerCompartment
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


# -- FleetMembership
class VehicleMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleMembership
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

# -- VehicleMembershipRequest
class VehicleMembershipRequestSerializer(serializers.ModelSerializer):
    carrier = CarrierSummarySerializer(source="vehicle.carrier",read_only=True,)
 #   vehicle = VehicleSummarySerializer(read_only=True,)
    class Meta:
        model = VehicleMembershipRequest
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
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["vehicle"] = VehicleSummarySerializer(
            instance.vehicle
        ).data

        return representation


# -- VehicleDocument
class VehicleDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleDocument
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




class VehicleManualDowntimeInputSerializer(
    serializers.Serializer,
):
    """
    Valide les données nécessaires à l’immobilisation
    manuelle d’un véhicule donné.
    """

    reason = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )

    start_date = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )
