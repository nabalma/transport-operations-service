from rest_framework import serializers

from apps.fleet.models import Carrier, CorrectiveAction, Defect, DefectReleaseValidation, Downtime, Evidence,Inspection, InspectionContextCriterion, InspectionContextSection, InspectionCriterion, InspectionCriterionResult, InspectionSection, Maintenance, NextTripEligibilityEvaluation, NextTripEligibilityEvaluationReason, ReturnToService, TankerCompartment, Vehicle, VehicleAvailabilityEvaluation, VehicleAvailabilityEvaluationReason, VehicleDocument, VehicleMembership, VehicleMembershipRequest

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

# -- InspectionSectionSummary
class InspectionSectionSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionSection
        fields = [
            "code",
            "title",
            "is_active",
        ]



# -- InspectionCriterionSummary
class InspectionCriterionSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionCriterion
        fields = [
            "code",
            "label",
            "scope",
            "is_active",
        ]


# -- InspectionContextSectionSummary
class InspectionContextSectionSummarySerializer(serializers.ModelSerializer):
    section = InspectionSectionSummarySerializer(read_only=True)

    class Meta:
        model = InspectionContextSection
        fields = [
            "context",
            "reference",
            "section",
        ]  

# -- InspectionContextCriterionSummary
class InspectionContextCriterionSummarySerializer(serializers.ModelSerializer):
    criterion = InspectionCriterionSummarySerializer(read_only=True,)

    class Meta:
        model = InspectionContextCriterion
        fields = [
            "reference",
            "criterion",
        ]

# -- InspectionSummary
class InspectionSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = [
            "context",
            "overall_result",
        ]


# -- InspectionCriterionResultSummary
class InspectionCriterionResultSummarySerializer(serializers.ModelSerializer):
    context_criterion = InspectionContextCriterionSummarySerializer(
        read_only=True,
    )

    class Meta:
        model = InspectionCriterionResult
        fields = [
            "context_criterion",
            "result",
        ]


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

# -- FleetMembership
class VehicleMembershipRequestSerializer(serializers.ModelSerializer):
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

# -- InspectionSection
class InspectionSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionSection
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



# -- InspectionCriterion
class InspectionCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionCriterion
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

 
# -- InspectionContextSection
class InspectionContextSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionContextSection
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


# -- InspectionContextCriterion
class InspectionContextCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionContextCriterion
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


# -- Inspection
class InspectionSerializer(serializers.ModelSerializer):
    criterion_results = InspectionCriterionResultSummarySerializer(many=True,read_only=True,)
    class Meta:
        model = Inspection
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

# -- InspectionCriterionResult
class InspectionCriterionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionCriterionResult
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


