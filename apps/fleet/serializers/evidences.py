from rest_framework import serializers
from apps.fleet.models import Evidence



# -- EvidenceSummary
class EvidenceSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = [
            "owner_type",
            "evidence_type",
            "file_url",
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
