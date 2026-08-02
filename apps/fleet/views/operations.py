
from apps.fleet.models import Downtime,ReturnToService,DowntimeCause
from apps.fleet.serializers import DowntimeSerializer, ReturnToServiceSerializer
from apps.fleet.serializers.operations import DowntimeCreateInputSerializer
from apps.fleet.services import create_manual_downtime
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
     

class ReturnToServiceViewSet(AuditUserMixin,SoftDeleteMixin, ModelViewSet,):
    queryset = (ReturnToService.objects
        .select_related("vehicle")
        .filter(is_deleted=False)
    )
    serializer_class = ReturnToServiceSerializer
  


