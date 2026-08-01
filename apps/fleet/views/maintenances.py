


from apps.fleet.models import MaintenanceSchedule,MaintenanceWorkOrder,MaintenancePolicy,MaintenanceComponent,MaintenanceWorkOrderItem


from rest_framework.viewsets import ModelViewSet
from apps.fleet.permissions import MaintenancePolicyPermission
from apps.fleet.serializers import MaintenanceWorkOrderItemCreateInputSerializer, MaintenanceScheduleGenerateWorkOrderInputSerializer,MaintenanceScheduleCancelInputSerializer,MaintenanceScheduleSerializer,MaintenanceWorkOrderCancelInputSerializer,MaintenanceWorkOrderCompleteInputSerializer,MaintenanceWorkOrderSerializer,MaintenanceWorkOrderItemSerializer,MaintenancePolicySerializer, MaintenanceComponentSerializer
from apps.fleet.services import generate_preventive_work_order,delete_maintenance_schedule,fulfill_maintenance_schedule,update_maintenance_schedule, cancel_maintenance_schedule,create_maintenance_schedule,delete_maintenance_work_order,cancel_maintenance_work_order,complete_maintenance_work_order,update_maintenance_work_order,create_maintenance_work_order,delete_maintenance_work_order_item,update_maintenance_work_order_item,create_maintenance_policy,create_maintenance_component,create_maintenance_work_order_item

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch


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





class MaintenanceWorkOrderViewSet(ModelViewSet):
    """
    API des ordres de travail de maintenance.
    """

    serializer_class = MaintenanceWorkOrderSerializer

    http_method_names = (
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "head",
    "options",
    )
    
    def get_queryset(self):
        return (
            MaintenanceWorkOrder.objects
    .filter(is_deleted=False)
    .select_related(
        "vehicle",
        "schedule",
        "defect",
        "created_by",
        "updated_by",
    )
    .prefetch_related(
        Prefetch(
            "items",
            queryset=(
                MaintenanceWorkOrderItem.objects
                .filter(is_deleted=False)
                .select_related("component")
                .order_by("created_at")
            ),
        ),
    )
    .order_by("-created_at")
        )

    def perform_create(self, serializer):
        work_order = create_maintenance_work_order(
            vehicle=serializer.validated_data["vehicle"],
            kind=serializer.validated_data["kind"],
            title=serializer.validated_data["title"],
            description=serializer.validated_data.get(
                "description",
                "",
            ),
            schedule=serializer.validated_data.get("schedule"),
            defect=serializer.validated_data.get("defect"),
            planned_start_at=serializer.validated_data.get(
                "planned_start_at"
            ),
            planned_end_at=serializer.validated_data.get(
                "planned_end_at"
            ),
            user=self.request.user,
        )

        serializer.instance = work_order


    def perform_update(self, serializer):
        """
        Met à jour un ordre de travail de maintenance.
        """

        work_order = serializer.instance

        work_order = update_maintenance_work_order(
            work_order=work_order,
            kind=serializer.validated_data.get(
                "kind",
                work_order.kind,
            ),
            title=serializer.validated_data.get(
                "title",
                work_order.title,
            ),
            description=serializer.validated_data.get(
                "description",
                work_order.description,
            ),
            schedule=serializer.validated_data.get(
                "schedule",
                work_order.schedule,
            ),
            defect=serializer.validated_data.get(
                "defect",
                work_order.defect,
            ),
            planned_start_at=serializer.validated_data.get(
                "planned_start_at",
                work_order.planned_start_at,
            ),
            planned_end_at=serializer.validated_data.get(
                "planned_end_at",
                work_order.planned_end_at,
            ),
            user=self.request.user,
        )

        serializer.instance = work_order

    def perform_destroy(
    self,
    instance: MaintenanceWorkOrder,
    ) -> None:
            """
            Supprime logiquement un ordre de travail.
            """

            delete_maintenance_work_order(
                work_order=instance,
                user=self.request.user,
            )


    @action(
        detail=True,
        methods=["post"],
        url_path="complete",
        serializer_class=MaintenanceWorkOrderCompleteInputSerializer,
    )
    def complete(
        self,
        request,
        pk=None,
    ):
        """
        Déclare un ordre de travail comme terminé.
        """

        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        work_order = complete_maintenance_work_order(
            work_order=self.get_object(),
            completion_notes=serializer.validated_data[
                "completion_notes"
            ],
            user=request.user,
        )

        output_serializer = MaintenanceWorkOrderSerializer(
            work_order,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_200_OK,
        )


    @action(
    detail=True,
    methods=["post"],
    url_path="cancel",
    serializer_class=MaintenanceWorkOrderCancelInputSerializer,
)
    def cancel(
    self,
    request,
    pk=None,
    ):
            """
            Annule un ordre de travail.
            """

            serializer = self.get_serializer(
                data=request.data,
            )

            serializer.is_valid(
                raise_exception=True,
            )

            work_order = cancel_maintenance_work_order(
                work_order=self.get_object(),
                cancellation_reason=serializer.validated_data[
                    "cancellation_reason"
                ],
                user=request.user,
            )

            output_serializer = MaintenanceWorkOrderSerializer(
                work_order,
            )

            return Response(
                output_serializer.data,
                status=status.HTTP_200_OK,
            )


    @action(
    detail=True,
    methods=["post"],
    url_path="items",
    serializer_class=MaintenanceWorkOrderItemCreateInputSerializer,
)
    def create_item(
    self,
    request,
    pk=None,
    ):
        """
        Ajoute une intervention à un ordre de travail donné.
        """

        work_order = self.get_object()

        serializer = MaintenanceWorkOrderItemSerializer(
            data={
                **request.data,
                "work_order": work_order.pk,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        item = create_maintenance_work_order_item(
            work_order=work_order,
            component=serializer.validated_data["component"],
            description=serializer.validated_data.get(
                "description",
                "",
            ),
            user=request.user,
        )

        output_serializer = MaintenanceWorkOrderItemSerializer(
            item,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )





class MaintenanceScheduleViewSet(ModelViewSet):
    """
    API des planifications de maintenance préventive.
    """

    serializer_class = MaintenanceScheduleSerializer

    http_method_names = (
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "head",
    "options",
)

    queryset = (
        MaintenanceSchedule.objects
        .filter(is_deleted=False)
        .select_related(
            "vehicle",
            "policy",
            "created_by",
            "updated_by",
        )
        .order_by(
            "due_at",
            "due_mileage",
            "due_engine_hours",
        )
    )

    def perform_create(self, serializer):
        """
        Crée une planification via le service métier.
        """

        schedule = create_maintenance_schedule(
            vehicle=serializer.validated_data["vehicle"],
            policy=serializer.validated_data["policy"],
            due_at=serializer.validated_data.get("due_at"),
            due_mileage=serializer.validated_data.get(
                "due_mileage",
            ),
            due_engine_hours=serializer.validated_data.get(
                "due_engine_hours",
            ),
            user=self.request.user,
        )

        serializer.instance = schedule


    @action(
    detail=True,
    methods=["post"],
    url_path="cancel",
    serializer_class=MaintenanceScheduleCancelInputSerializer,
    )
    def cancel(
    self,
    request,
    pk=None,
    ):
            """
            Annule une planification de maintenance active.
            """

            serializer = self.get_serializer(
                data=request.data,
            )
            serializer.is_valid(
                raise_exception=True,
            )

            schedule = cancel_maintenance_schedule(
                schedule=self.get_object(),
                cancellation_reason=serializer.validated_data[
                    "cancellation_reason"
                ],
                user=request.user,
            )

            output_serializer = MaintenanceScheduleSerializer(
                schedule,
            )

            return Response(
                output_serializer.data,
                status=status.HTTP_200_OK,
            )



    def perform_update(
    self,
    serializer: MaintenanceScheduleSerializer,
    ) -> None:
            """
            Met à jour les échéances via le service métier.
            """

            schedule = serializer.instance

            updated_schedule = update_maintenance_schedule(
                schedule=schedule,
                due_at=serializer.validated_data.get(
                    "due_at",
                    schedule.due_at,
                ),
                due_mileage=serializer.validated_data.get(
                    "due_mileage",
                    schedule.due_mileage,
                ),
                due_engine_hours=serializer.validated_data.get(
                    "due_engine_hours",
                    schedule.due_engine_hours,
                ),
                user=self.request.user,
            )

            serializer.instance = updated_schedule

    @action(
    detail=True,
    methods=["post"],
    url_path="fulfill",
)
    def fulfill(
            self,
            request,
            pk=None,
    ):
            """
            Déclare une planification de maintenance comme réalisée.
            """

            schedule = fulfill_maintenance_schedule(
                schedule=self.get_object(),
                user=request.user,
            )

            output_serializer = MaintenanceScheduleSerializer(
                schedule,
            )

            return Response(
                output_serializer.data,
                status=status.HTTP_200_OK,
            )


    def perform_destroy(
    self,
    instance: MaintenanceSchedule,
) -> None:
        """
        Supprime logiquement une planification de maintenance.
        """

        delete_maintenance_schedule(
            schedule=instance,
            user=self.request.user,
        )



    @action(
    detail=True,
    methods=["post"],
    url_path="generate-work-order",
    serializer_class=MaintenanceScheduleGenerateWorkOrderInputSerializer,
)
    def generate_work_order(
    self,
    request,
    pk=None,
):
            """
            Génère un ordre de travail préventif depuis une planification.
            """

            serializer = self.get_serializer(
                data=request.data,
            )
            serializer.is_valid(
                raise_exception=True,
            )

            work_order = generate_preventive_work_order(
                schedule=self.get_object(),
                title=serializer.validated_data["title"],
                description=serializer.validated_data.get(
                    "description",
                    "",
                ),
                planned_start_at=serializer.validated_data.get(
                    "planned_start_at",
                ),
                planned_end_at=serializer.validated_data.get(
                    "planned_end_at",
                ),
                user=request.user,
            )

            output_serializer = MaintenanceWorkOrderSerializer(
                work_order,
            )

            return Response(
                output_serializer.data,
                status=status.HTTP_201_CREATED,
            )