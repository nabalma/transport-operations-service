


from apps.fleet.models import MaintenancePolicy
from rest_framework.viewsets import ModelViewSet
from apps.fleet.permissions import MaintenancePolicyPermission
from apps.fleet.serializers import MaintenancePolicySerializer
from apps.fleet.services import create_maintenance_policy


class MaintenancePolicyViewSet(ModelViewSet):
    """
    Expose les opérations CRUD des politiques de maintenance.
    """

    queryset = MaintenancePolicy.objects.all()
    serializer_class = MaintenancePolicySerializer
    permission_classes = [MaintenancePolicyPermission]

    def perform_create(self,serializer):
        policy = create_maintenance_policy(
            user=self.request.user,
            **serializer.validated_data,
        )
        serializer.instance = policy