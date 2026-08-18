
from apps.fleet.permissions import VehicleAvailabilityEvaluationReasonPermission, VehicleAvailabilityEvaluationPermission 
from apps.fleet.serializers.availabilities import VehicleAvailabilityValidationInputSerializer
from apps.fleet.services.availabilities import validate_vehicle_availability_evaluation


from apps.fleet.selectors import list_vehicle_availability_evaluations
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.fleet.models import VehicleAvailabilityEvaluationReason
from apps.fleet.serializers import VehicleAvailabilityEvaluationReasonSerializer, VehicleAvailabilityEvaluationSerializer 

from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response

class VehicleAvailabilityEvaluationViewSet(ReadOnlyModelViewSet):
    queryset = list_vehicle_availability_evaluations()
    serializer_class = VehicleAvailabilityEvaluationSerializer
    permission_classes = [VehicleAvailabilityEvaluationPermission]

    @action(
    detail=True,
    methods=["post"],
    url_path="validate",
    serializer_class=VehicleAvailabilityValidationInputSerializer,
    )
    def validate_evaluation(
    self,
    request,
    pk=None,
):
            """
            Confirme ou modifie le résultat final
            d’une évaluation de disponibilité.
            """

            serializer = self.get_serializer(
                data=request.data,
            )
            serializer.is_valid(
                raise_exception=True,
            )

            evaluation = validate_vehicle_availability_evaluation(
                evaluation=self.get_object(),
                final_result=serializer.validated_data["final_result"],
                validation_comment=serializer.validated_data.get(
                    "validation_comment",
                ),
                user=request.user,
            )

            output_serializer = VehicleAvailabilityEvaluationSerializer(
                evaluation,
            )

            return Response(
                output_serializer.data,
                status=status.HTTP_200_OK,
            )
        

class VehicleAvailabilityEvaluationReasonViewSet(ReadOnlyModelViewSet,):
    queryset = (
        VehicleAvailabilityEvaluationReason.objects
        .select_related(
            "evaluation",
            "evaluation__vehicle",
        )
        .filter(is_deleted=False)
    )
    serializer_class = VehicleAvailabilityEvaluationReasonSerializer
    permission_classes = [VehicleAvailabilityEvaluationReasonPermission]
  











  



  