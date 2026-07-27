


from rest_framework import status
from rest_framework.response import Response
from apps.fleet.services import submit_defect_release_request, validate_defect_release_request

from .mixins import AuditUserMixin, SoftDeleteMixin
from apps.fleet.selectors import list_defects_with_source_and_resolution
from rest_framework.viewsets import ModelViewSet,ReadOnlyModelViewSet
from apps.fleet.models import DefectReleaseValidation,DefectReleaseRequest
from apps.fleet.serializers import DefectReleaseValidationSerializer, DefectSerializer,DefectReleaseRequestSubmitSerializer,DefectReleaseRequestSerializer,DefectReleaseValidationInputSerializer
from rest_framework.decorators import action


class DefectViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = list_defects_with_source_and_resolution()
    serializer_class = DefectSerializer

        # submit_release_request
    # Soumet une demande de levée pour le défaut sélectionné.
    @action(
        detail=True,
        methods=["post"],
        url_path="submit-release-request",
        serializer_class=DefectReleaseRequestSubmitSerializer,
    )
    def submit_release_request(self, request, pk=None):
        """
        Valide les données reçues et soumet le défaut pour validation.
        """
        defect = self.get_object()

        input_serializer = self.get_serializer(
            data=request.data,
        )
        input_serializer.is_valid(raise_exception=True)

        release_request = submit_defect_release_request(
            defect=defect,
            correction_summary=input_serializer.validated_data[
                "correction_summary"
            ],
            submitted_by=request.user,
        )

        output_serializer = DefectReleaseRequestSerializer(
            release_request,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )



# Voir la raison du ReadoOnlyModelViewset 
# DefectReleaseRequestViewSet
# Expose les demandes de levée en lecture seule.
class DefectReleaseRequestViewSet(ReadOnlyModelViewSet):
    """
    Permet de consulter la liste et le détail des demandes de levée.
    """

    serializer_class = DefectReleaseRequestSerializer
    queryset = (
        DefectReleaseRequest.objects
        .filter(is_deleted=False)
        .select_related(
            "defect",
            "submitted_by",
        )
        .order_by("-submitted_at")
    )

        # validate
    # Enregistre la décision finale sur une demande de levée.
    @action(
        detail=True,
        methods=["post"],
        url_path="validate",
        serializer_class=DefectReleaseValidationInputSerializer,
    )
    def validate(self, request, pk=None):
        """
        Valide la demande de levée sélectionnée.
        """
        release_request = self.get_object()

        input_serializer = self.get_serializer(
            data=request.data,
        )
        input_serializer.is_valid(raise_exception=True)

        validation = validate_defect_release_request(
            release_request=release_request,
            decision=input_serializer.validated_data["decision"],
            comment=input_serializer.validated_data.get("comment"),
            validated_by=request.user,
        )

        output_serializer = DefectReleaseValidationSerializer(
            validation,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )



class DefectReleaseValidationViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = (DefectReleaseValidation.objects
        .select_related("defect")
        .filter(is_deleted=False))
    serializer_class = DefectReleaseValidationSerializer
  