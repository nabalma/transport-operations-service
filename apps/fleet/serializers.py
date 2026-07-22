from apps.fleet.constants import InspectionContext, InspectionCriterionResultValue, InspectionLocationType
from rest_framework import serializers

from apps.fleet.models import Carrier, CorrectiveAction, Defect, DefectReleaseValidation, Downtime, Evidence,Inspection, InspectionChapter,InspectionCriterion, InspectionCriterionResult, InspectionScoringPolicyConfiguration, InspectionSection, InspectionVersion, Maintenance, NextTripEligibilityEvaluation, NextTripEligibilityEvaluationReason, ReturnToService, TankerCompartment, Vehicle, VehicleAgePolicyConfiguration, VehicleAvailabilityEvaluation, VehicleAvailabilityEvaluationReason, VehicleDocument, VehicleMembership, VehicleMembershipRequest

# -------------------------
# --- SUMMARY SERIALIZERS
#------------------------- 
# ---Carrier Summary 
class CarrierSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = [
            "id",
            "name",
        ]

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


# =============================================================================
# InspectionSectionSummarySerializer
#
# Représentation légère d’une section dans les réponses imbriquées.
# =============================================================================
class InspectionSectionSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionSection
        fields = (
            "id",
            "reference",
            "code",
            "title",
            "is_active",
        )


# =============================================================================
# InspectionCriterionSummarySerializer
#
# Représentation légère d’un critère appartenant à une section versionnée.
# =============================================================================
class InspectionCriterionSummarySerializer(serializers.ModelSerializer):
    section = InspectionSectionSummarySerializer(
        read_only=True,
    )

    class Meta:
        model = InspectionCriterion
        fields = (
            "id",
            "section",
            "reference",
            "code",
            "label",
            "creates_defect_if_failed",
            "is_blocking_if_failed",
            "is_active",
        )


# =============================================================================
# InspectionCriterionResultSummarySerializer
#
# Représentation légère du résultat d’un critère dans une inspection.
#
# Le résultat pointe directement vers InspectionCriterion.
# =============================================================================
class InspectionCriterionResultSummarySerializer(
    serializers.ModelSerializer
):
    criterion = InspectionCriterionSummarySerializer(
        read_only=True,
    )

    class Meta:
        model = InspectionCriterionResult
        fields = (
            "id",
            "criterion",
            "result",
            "comment",
        )




# -- DefectSummary
class DefectSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Defect
        fields = [
            "scope",
            "description",
            "severity",
            "is_blocking",
            "status",
        ]




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


# -- MaintenanceSummary
class MaintenanceSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintenance
        fields = [
          
            "scope",
            "type",
            "status",
        ]

# -- DowntimeSummary
class DowntimeSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Downtime
        fields = [
            "source_type",
            "status",
        ]


# -- VehicleAvailabilityEvaluationSummary
class VehicleAvailabilityEvaluationSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleAvailabilityEvaluation
        fields = [
            "id",
            "calculated_result",
            "final_result",          
        ]

# -- VehicleAvailabilityEvaluationReasonSummary
class VehicleAvailabilityEvaluationReasonSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleAvailabilityEvaluationReason
        fields = [
            "reason_type",
            "message",
            "source_id",
        ]



# -- NextTripEligibilityEvaluationSummary
class NextTripEligibilityEvaluationSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = NextTripEligibilityEvaluation
        fields = [
            "id",
            "reason_type",
            "message",
            "source_id",
        ]


# -- NextTripEligibilityEvaluationReasonSummary
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

# -- EvidenceSummary
class EvidenceSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = [
            "owner_type",
            "evidence_type",
            "file_url",
        ]





# -------------------------
# --- FULL SERIALIZERS
#------------------------- 

# --- Carrier 
class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = "__all__"


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


# -- InspectionScoringPolicyConfiguration
class InspectionScoringPolicyConfigurationSerializer(serializers.ModelSerializer,):
    class Meta:
        model = InspectionScoringPolicyConfiguration
        fields = "__all__"

        read_only_fields = [
            "id",
            "activated_at",
            "retired_at",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
            "is_deleted",
            "deleted_at",
            "deleted_by",
        ]


# =============================================================================
# InspectionContextVersionSerializer
#
# Gère une version complète d’un formulaire d’inspection.
#
# Après création, les champs context, version et source_version sont
# immuables. Seul is_current peut être modifié.
# =============================================================================
class InspectionVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionVersion
        fields = (
            "id",
            "context",
            "version",
            "source_version",
            "is_current",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )

        read_only_fields = (
            "id",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )

    def validate(self, attrs):
        if self.instance is None:
            return attrs

        immutable_fields = (
            "context",
            "version",
            "source_version",
        )

        modified_fields = [
            field
            for field in immutable_fields
            if field in attrs
            and attrs[field] != getattr(self.instance, field)
        ]

        if modified_fields:
            raise serializers.ValidationError(
                {
                    field: "Ce champ ne peut pas être modifié."
                    for field in modified_fields
                }
            )

        return attrs


# InspectionChapterSerializer
# Sérialise les chapitres d’une version d’inspection.
# Expose les champs nécessaires à leur gestion via l’API.
class InspectionChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionChapter
        fields = (
            "id",
            "position",
            "inspection_version",
            "reference",
            "code",
            "title",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


# =============================================================================
# InspectionSectionSerializer
#
# Gère les sections appartenant directement à une version d’inspection.
# =============================================================================
class InspectionSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionSection
        fields = (
            "id",
            "position",
            "chapter",
            "reference",
            "code",
            "title",
            "is_active",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )

        read_only_fields = (
            "id",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )


# =============================================================================
# InspectionCriterionSerializer
#
# Gère les critères appartenant directement à une section versionnée.
# =============================================================================
class InspectionCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionCriterion
        fields = (
            "id",
            "section",
            "reference",
            "position",
            "code",
            "label",
            "creates_defect_if_failed",
            "is_blocking_if_failed",
            "is_active",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )

        read_only_fields = (
            "id",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )

# RecordCriterionResultInputSerializer
# Validates the input required to record one criterion result.
class RecordCriterionResultInputSerializer(serializers.Serializer):
    criterion_id = serializers.UUIDField()

    result = serializers.ChoiceField(
        choices=InspectionCriterionResultValue.choices,
    )

    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )


# =============================================================================
# InspectionSerializer
#
# Gère une inspection réelle et expose les résultats des critères
# en lecture seule.
# =============================================================================
class InspectionSerializer(serializers.ModelSerializer):
    criterion_results = InspectionCriterionResultSummarySerializer(
        many=True,
        read_only=True,
    )

    context = serializers.CharField(
        source="inspection_version.context",
        read_only=True,
    )

    class Meta:
        model = Inspection
        fields = (
            "id",
            "vehicle",
            "inspection_version",
            "context",
            "inspection_date",
            "inspector",
            "status",
            "overall_result",
            "comments",
            "criterion_results",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )

        read_only_fields = (
            "id",
            "context",
            "criterion_results",
            "status",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )


# CreateInspectionSerializer
# Validates the data required to start an inspection.
class CreateInspectionSerializer(serializers.Serializer):
    vehicle_id = serializers.UUIDField()
    inspection_context = serializers.CharField()





# =============================================================================
# InspectionCriterionResultSerializer
#
# Gère le résultat d’un critère pour une inspection.
#
# Vérifie que le critère appartient à la même version que l’inspection.
# =============================================================================
class InspectionCriterionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionCriterionResult
        fields = (
            "id",
            "inspection",
            "criterion",
            "result",
            "comment",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )

        read_only_fields = (
            "id",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )

    def validate(self, attrs):
        inspection = attrs.get(
            "inspection",
            getattr(self.instance, "inspection", None),
        )

        criterion = attrs.get(
            "criterion",
            getattr(self.instance, "criterion", None),
        )

        if inspection is None or criterion is None:
            return attrs

        criterion_version_id = (
            criterion.section.chapter.inspection_version_id
        )

        if criterion_version_id != inspection.inspection_version_id:
            raise serializers.ValidationError(
                {
                    "criterion": (
                        "Le critère n’appartient pas à la version "
                        "utilisée par cette inspection."
                    ),
                }
            )

        return attrs
    

# -------------------------------------------------------------------
# InspectionLocationInputSerializer
# Données décrivant le lieu où l'inspection est effectuée.
# -------------------------------------------------------------------
class InspectionLocationInputSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=InspectionLocationType.choices,)
    name = serializers.CharField(max_length=255,)



# -------------------------------------------------------------------
# GenerateInspectionSheetInputSerializer
# Données requises pour générer une fiche d’inspection vierge.
# -------------------------------------------------------------------
class GenerateInspectionSheetInputSerializer(serializers.Serializer):
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(),)
    inspection_type = serializers.ChoiceField(choices=InspectionContext.choices,)
    inspection_date = serializers.DateField()
    location = InspectionLocationInputSerializer()




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


# -- Maintenance
class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintenance
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

# -- Downtime
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

# -- ReturnToService
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


# -- ReturnToServiceSummary
class ReturnToServiceSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnToService
        fields = [
            "source_type",
            "proposed_by_system",
            "decision",
        ]

# -- VehicleAvailabilityEvaluation
class VehicleAvailabilityEvaluationSerializer(serializers.ModelSerializer):
    evaluation_reasons = VehicleAvailabilityEvaluationReasonSummarySerializer(many=True,read_only=True,)

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


# -- VehicleAvailabilityEvaluationReason
class VehicleAvailabilityEvaluationReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleAvailabilityEvaluationReason
        fields = "__all__"

        read_only_fields = [
            "id",
            "created_at",
        ]


# -- NextTripEligibilityEvaluation
class NextTripEligibilityEvaluationSerializer(serializers.ModelSerializer):
    evaluation_reasons = NextTripEligibilityEvaluationReasonSummarySerializer(many=True,read_only=True,)
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


# -- NextTripEligibilityEvaluationReason
class NextTripEligibilityEvaluationReasonSerializer(serializers.ModelSerializer):
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

# -- Evidence
class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
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
