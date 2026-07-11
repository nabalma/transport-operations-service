from rest_framework.viewsets import ModelViewSet

from apps.fleet.models import Carrier
from apps.fleet.serializers import CarrierSerializer


class CarrierViewSet(ModelViewSet):
    queryset = Carrier.objects.all()
    serializer_class = CarrierSerializer