from rest_framework import serializers
from apps.fleet.models import Carrier


class CarrierSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = [
            "id",
            "name",
        ]


# --- Carrier 
class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = "__all__"
