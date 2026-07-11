from rest_framework import serializers

from apps.fleet.models import Carrier


class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = "__all__"