


from apps.fleet.models import MaintenancePolicy,MaintenanceComponent,MaintenanceWorkOrderItem

from rest_framework.viewsets import ModelViewSet
from apps.fleet.permissions import MaintenancePolicyPermission
from apps.fleet.serializers import MaintenanceWorkOrderItemSerializer,MaintenancePolicySerializer, MaintenanceComponentSerializer
from apps.fleet.services import delete_maintenance_work_order_item,update_maintenance_work_order_item,create_maintenance_policy,create_maintenance_component,create_maintenance_work_order_item


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
    permission_classes = [MaintenancePolicyPermission]

    def perform_create(self, serializer):
        component = create_maintenance_component(
            user=self.request.user,
            **serializer.validated_data,
        )

        serializer.instance = component



class MaintenanceWorkOrderItemViewSet(
    ModelViewSet,
):
    """
    API CRUD des interventions appartenant aux ordres de travail.
    """
    #Pas de put, ni  de patch permis ....
    http_method_names = (
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "head",
    "options",
    )

    serializer_class = MaintenanceWorkOrderItemSerializer

    queryset = (
    MaintenanceWorkOrderItem.objects
    .filter(is_deleted=False)
    .select_related(
        "work_order",
        "component",
        "created_by",
        "updated_by",
    )
    .order_by("-created_at")
    )

    def perform_create(
        self,
        serializer: MaintenanceWorkOrderItemSerializer,
    ) -> None:
        """
        Crée l'intervention à travers le service métier.
        """

        item = create_maintenance_work_order_item(
            work_order=serializer.validated_data["work_order"],
            component=serializer.validated_data["component"],
            description=serializer.validated_data.get(
                "description",
                "",
            ),
            user=self.request.user,
        )

        serializer.instance = item


    def perform_update(
        self,
        serializer: MaintenanceWorkOrderItemSerializer,
    ) -> None:
        """
        Met à jour une intervention à travers le service métier.

        Lors d'une mise à jour partielle, les champs absents conservent
        leur valeur actuelle.
        """

        item = serializer.instance

        updated_item = update_maintenance_work_order_item(
            item=item,
            component=serializer.validated_data.get(
                "component",
                item.component,
            ),
            description=serializer.validated_data.get(
                "description",
                item.description,
            ),
            user=self.request.user,
        )

        serializer.instance = updated_item

    def perform_destroy(
    self,
    instance: MaintenanceWorkOrderItem,
) -> None:
        """
        Supprime logiquement une intervention via le service métier.
        """

        delete_maintenance_work_order_item(
            item=instance,
            user=self.request.user,
        )