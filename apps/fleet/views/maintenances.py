


from apps.fleet.models import MaintenancePolicy,MaintenanceComponent
from rest_framework.viewsets import ModelViewSet
from apps.fleet.permissions import MaintenancePolicyPermission
from apps.fleet.serializers import MaintenancePolicySerializer, MaintenanceComponentSerializer
from apps.fleet.services import create_maintenance_policy,create_maintenance_component


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


class MaintenanceComponentViewSet(ModelViewSet):
    """
    API CRUD du catalogue des composants de maintenance.
    """

    queryset = MaintenanceComponent.objects.filter(
        is_deleted=False,
    ).order_by(
        "scope",
        "name",
    )

    serializer_class = MaintenanceComponentSerializer

    def perform_create(self, serializer):
        component = create_maintenance_component(
            user=self.request.user,
            **serializer.validated_data,
        )

        serializer.instance = component