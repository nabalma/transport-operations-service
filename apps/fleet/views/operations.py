
from apps.fleet.models import Downtime,ReturnToService,DowntimeCause
from apps.fleet.serializers import DowntimeSerializer, ReturnToServiceSerializer
from apps.fleet.serializers.operations import DowntimeCauseSerializer, DowntimeCreateInputSerializer, ReturnToServiceCreateInputSerializer
from apps.fleet.services import create_manual_downtime
from apps.fleet.services.downtimes import resolve_downtime_cause
from apps.fleet.services.return_to_services import create_return_to_service
from .mixins import AuditUserMixin, SoftDeleteMixin
from rest_framework.viewsets import ModelViewSet

from django.db.models import Prefetch
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response


class DowntimeViewSet(AuditUserMixin,SoftDeleteMixin, ModelViewSet,):
    """
    API des immobilisations de véhicules.
    """

    serializer_class = DowntimeSerializer

    queryset = (
        Downtime.objects
        .filter(is_deleted=False)
        .select_related(
            "vehicle",
            "created_by",
            "updated_by",
        )
        .prefetch_related(
            Prefetch(
                "causes",
                queryset=(
                    DowntimeCause.objects
                    .filter(is_deleted=False)
                    .select_related(
                        "inspection_criterion_result",
                        "defect",
                        "resolved_by",
                        "created_by",
                    )
                    .order_by("created_at")
                ),
            )
        )
        .order_by("-start_date")
    )

    @action(
    detail=False,
    methods=["post"],
    url_path="manual",
    serializer_class=DowntimeCreateInputSerializer,
    )
    def create_manual(self, request):
        serializer = self.get_serializer(
        data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )
        downtime = create_manual_downtime(
        vehicle=serializer.validated_data["vehicle"],
        reason=serializer.validated_data["reason"],
        start_date=serializer.validated_data.get("start_date"),
        user=request.user,
        )

        output_serializer = DowntimeSerializer(
        downtime,
        )

        return Response(
        output_serializer.data,
        status=status.HTTP_201_CREATED,
       )


    @action(
    detail=True,
    methods=["post"],
    url_path="return-to-service",
    serializer_class=ReturnToServiceCreateInputSerializer,
)
    def create_return_to_service_action(
    self,
    request,
    pk=None,
):
            """
            Crée une demande de remise en service
            pour cette immobilisation.
            """

            downtime = self.get_object()

            serializer = self.get_serializer(
                data=request.data,
            )
            serializer.is_valid(
                raise_exception=True,
            )

            return_to_service = create_return_to_service(
                downtime=downtime,
                source_type=serializer.validated_data["source_type"],
                source_id=serializer.validated_data.get("source_id"),
                proposed_by_system=serializer.validated_data.get(
                    "proposed_by_system",
                    False,
                ),
                user=request.user,
            )

            output_serializer = ReturnToServiceSerializer(
                return_to_service,
            )

            return Response(
                output_serializer.data,
                status=status.HTTP_201_CREATED,
            )




class DowntimeCauseViewSet(ModelViewSet):
    """
    API des causes d’immobilisation.
    """

    serializer_class = DowntimeCauseSerializer

    queryset = (
        DowntimeCause.objects
        .filter(is_deleted=False)
        .select_related(
            "downtime",
            "defect",
            "inspection_criterion_result",
            "resolved_by",
            "created_by",
            "updated_by",
        )
        .order_by("-created_at")
    )

    @action(
    detail=True,
    methods=["post"],
    url_path="resolve",
)
    def resolve(
    self,
    request,
    pk=None,
    ):
            """
            Marque cette cause d’immobilisation comme résolue.
            """

            cause = resolve_downtime_cause(
                cause=self.get_object(),
                user=request.user,
            )

            serializer = DowntimeCauseSerializer(
                cause,
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )




    

class ReturnToServiceViewSet(AuditUserMixin,SoftDeleteMixin, ModelViewSet,):
    queryset = (ReturnToService.objects
        .select_related("vehicle")
        .filter(is_deleted=False)
    )
    serializer_class = ReturnToServiceSerializer
  


