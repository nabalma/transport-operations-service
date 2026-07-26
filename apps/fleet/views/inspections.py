
from .mixins import AuditUserMixin, SoftDeleteMixin
from apps.fleet.permissions import InspectionConfigurationPermission, InspectionPermission
from apps.fleet.selectors import _get_inspection_criterion_or_error, _get_vehicle_or_error, list_inspections_with_results
from apps.fleet.services.inspections import activate_inspection_scoring_policy, build_blank_inspection_sheet, cancel_inspection, complete_inspection, create_inspection, create_inspection_version, record_criterion_result, update_inspection_version_status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response

from apps.fleet.models import InspectionChapter, InspectionCriterion, InspectionCriterionResult, InspectionScoringPolicyConfiguration, InspectionSection, InspectionVersion
from apps.fleet.serializers import CreateInspectionSerializer, InspectionChapterSerializer, InspectionScoringPolicyConfigurationSerializer, InspectionVersionSerializer, InspectionCriterionResultSerializer, InspectionCriterionSerializer, InspectionSectionSerializer, InspectionSerializer, InspectionVersionSerializer, RecordCriterionResultInputSerializer



# InspectionScoringPolicyConfigurationViewSet
# Manages inspection scoring policy configurations.
class InspectionScoringPolicyConfigurationViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = (InspectionScoringPolicyConfiguration.objects.filter(is_deleted=False))
    serializer_class = InspectionScoringPolicyConfigurationSerializer
    permission_classes = [InspectionConfigurationPermission,]

    # activate
    # Activates the selected scoring policy.
    @action(detail=True,methods=["post"],)
    def activate(self, request, pk=None):
        """
        Activate the selected scoring policy.
        """
        policy = self.get_object()
        policy = activate_inspection_scoring_policy(policy=policy,user=request.user,)
        serializer = self.get_serializer(policy)
        return Response(serializer.data)


class InspectionVersionViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = InspectionVersion.objects.filter(is_deleted=False)
    serializer_class = InspectionVersionSerializer
    permission_classes = [InspectionConfigurationPermission]

    def perform_create(self, serializer):
        serializer.instance = create_inspection_version(
            context=serializer.validated_data["context"],
            version=serializer.validated_data["version"],
            source_version=serializer.validated_data.get("source_version"),
            is_current=serializer.validated_data.get("is_current", False),
            created_by=self.request.user,
        )
    def perform_update(self, serializer):
        serializer.instance = update_inspection_version_status(
            inspection_version=serializer.instance,
            is_current=serializer.validated_data["is_current"],
            updated_by=self.request.user,
    )
        

# InspectionChapterViewSet
# Gère les opérations CRUD sur les chapitres d’inspection.
# Exclut les chapitres supprimés.
class InspectionChapterViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = InspectionChapter.objects.select_related("inspection_version",).filter(is_deleted=False,)
    serializer_class = InspectionChapterSerializer
    permission_classes = [InspectionConfigurationPermission]




# InspectionSectionViewSet
# Gère les sections directement rattachées à une version.
class InspectionSectionViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = InspectionSection.objects.select_related("chapter").filter(is_deleted=False)
    serializer_class = InspectionSectionSerializer
    permission_classes = [InspectionConfigurationPermission]



# InspectionCriterionViewSet
# Gère les critères directement rattachés à une section versionnée.
class InspectionCriterionViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = InspectionCriterion.objects.select_related("section","section__chapter",).filter(is_deleted=False)
    serializer_class = InspectionCriterionSerializer
    permission_classes = [InspectionConfigurationPermission]


# =============================================================================
# InspectionViewSet
#
# Charge la version utilisée et les résultats avec leurs critères.
# =============================================================================
class InspectionViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = list_inspections_with_results()

    serializer_class = InspectionSerializer
    permission_classes = [InspectionPermission]

    # blank_sheet
    # Retourne une fiche vierge pour le contexte d’inspection demandé.
    # La version courante est automatiquement sélectionnée par le service.
    @action(detail=False,methods=["get"],url_path="blank-sheet",)
    def blank_sheet(self, request):
        """
        Construit et retourne une fiche d’inspection vierge.
        Le contexte est lu depuis les paramètres de l’URL.
        """
        inspection_context=request.query_params.get("context")
        sheet = build_blank_inspection_sheet(inspection_context=inspection_context,)

        return Response(sheet,status=status.HTTP_200_OK,)
    
    # start_inspection
    # Creates a new inspection for the selected vehicle.
    # Uses the authenticated user as the inspector.
    @action(detail=False,methods=["post"],url_path="start-inspection",serializer_class=CreateInspectionSerializer,)
    def start_inspection(self, request):
        """
        Create a new inspection with the IN_PROGRESS status.
        The selected vehicle and inspection context are provided by the client.
        The authenticated user is automatically assigned as the inspector.
        """
        serializer = CreateInspectionSerializer(data=request.data,)
        serializer.is_valid(raise_exception=True,)
        context = serializer.validated_data["inspection_context"]
        vehicle = _get_vehicle_or_error(vehicle_id=serializer.validated_data["vehicle_id"],)

        inspection = create_inspection(
            vehicle=vehicle,
            inspection_context=context,
            inspector=request.user,
            )
        return Response(
            InspectionSerializer(inspection).data,
            status=status.HTTP_201_CREATED,)
 

    # cancel
    # Cancels an inspection currently in progress.
    # Delegates all business rules to the service layer.
    @action(detail=True,methods=["post"],url_path="cancel",)
    def cancel(self, request, pk=None):
        """
        Cancel the selected inspection.
        """
        inspection = self.get_object()
        inspection = cancel_inspection(inspection=inspection,user=request.user,)
        serialiser = self.get_serializer(inspection)

        return Response(serialiser.data,status=status.HTTP_200_OK,)
    

    @action(detail=True,methods=["post"],url_path="record-criterion-result",serializer_class=RecordCriterionResultInputSerializer,)
    def record_result(self, request, pk=None):
        """
        Record the result of one criterion for an inspection.
        """
        inspection = self.get_object()
        input_serializer = self.get_serializer(data=request.data,)
        input_serializer.is_valid(raise_exception=True,)
        criterion = _get_inspection_criterion_or_error(criterion_id=input_serializer.validated_data["criterion_id"],)
        criterion_result = record_criterion_result(
            inspection=inspection,
            criterion=criterion,
            result=input_serializer.validated_data["result"],
            comment=input_serializer.validated_data.get("comment"),
            user=request.user,
            )
        output_serializer = InspectionCriterionResultSerializer(criterion_result,)
        return Response(output_serializer.data,status=status.HTTP_201_CREATED,)

    # complete
# Completes an inspection after validating all business rules.
    @action(detail=True,methods=["post"],url_path="complete",)
    def complete(self,request,pk=None,):
        """
        Complete an inspection and return the updated inspection.
        """
        inspection = self.get_object()
        inspection = complete_inspection(inspection=inspection,user=request.user,)
        serializer = self.get_serializer(inspection,)

        return Response(serializer.data,status=status.HTTP_200_OK,)



# InspectionCriterionResultViewSet
# Charge directement le critère, sa section et sa version.
class InspectionCriterionResultViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = InspectionCriterionResult.objects.select_related(
            "inspection",
            "inspection__inspection_version",
            "criterion",
            "criterion__section",
            "criterion__section",
        ).filter(is_deleted=False)
    serializer_class = InspectionCriterionResultSerializer
    permission_classes = [InspectionPermission]
