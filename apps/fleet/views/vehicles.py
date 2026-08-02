from apps.fleet.filters import VehicleFilter
from apps.fleet.serializers.operations import DowntimeSerializer
from apps.fleet.serializers.vehicles import VehicleManualDowntimeInputSerializer
from apps.fleet.services.downtimes import create_manual_downtime
from .mixins import AuditUserMixin, SoftDeleteMixin
from apps.fleet.permissions import VehicleAgePolicyConfigurationPermission, VehicleMembershipPermission, VehicleMembershipRequestPermission, VehiclePermission
from apps.fleet.selectors import list_active_fleet_vehicles, list_vehicle_membership_requests, list_vehicles
from apps.fleet.services.membership import approve_vehicle_membership_request, cancel_vehicle_membership_request, create_vehicle_membership_request, reject_vehicle_membership_request, submit_vehicle_membership_request
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend



from apps.fleet.models import  TankerCompartment, VehicleAgePolicyConfiguration, VehicleDocument, VehicleMembership
from apps.fleet.serializers import TankerCompartmentSerializer, VehicleAgePolicyConfigurationSerializer,VehicleDocumentSerializer, VehicleMembershipRequestSerializer, VehicleMembershipSerializer, VehicleSerializer



class VehicleAgePolicyConfigurationViewSet(AuditUserMixin,ModelViewSet,):
    queryset = VehicleAgePolicyConfiguration.objects.all()
    serializer_class = VehicleAgePolicyConfigurationSerializer
    permission_classes = [VehicleAgePolicyConfigurationPermission]

    
       

class VehicleViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet):
   queryset = list_vehicles()
   serializer_class = VehicleSerializer
   permission_classes=[VehiclePermission]

   filter_backends = [DjangoFilterBackend]
   filterset_class = VehicleFilter


   @action(detail=False, methods=["get"], url_path="in-fleet")
   def in_fleet(self, request):
        queryset = list_active_fleet_vehicles()
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

   @action(
    detail=True,
    methods=["post"],
    url_path="downtimes/manual",
    serializer_class=VehicleManualDowntimeInputSerializer,
)
   def create_manual_downtime(
        self,
        request,
        pk=None,
    ):
        """
        Crée une immobilisation manuelle pour ce véhicule.
        """

        vehicle = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        downtime = create_manual_downtime(
            vehicle=vehicle,
            reason=serializer.validated_data["reason"],
            start_date=serializer.validated_data.get(
                "start_date",
            ),
            user=request.user,
        )

        output_serializer = DowntimeSerializer(
            downtime,
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class TankerCompartmentViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = TankerCompartment.objects.filter(is_deleted=False)
    serializer_class = TankerCompartmentSerializer
    permission_classes=[VehiclePermission]
  

class VehicleMembershipViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = VehicleMembership.objects.filter(is_deleted=False)
    serializer_class = VehicleMembershipSerializer
    permission_classes =[VehicleMembershipPermission]
  

class VehicleMembershipRequestViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = list_vehicle_membership_requests()
    serializer_class = VehicleMembershipRequestSerializer
    permission_classes =[VehicleMembershipRequestPermission]


    # action pour la creation de la request
    def perform_create(self, serializer):
        membership_request = create_vehicle_membership_request(
            vehicle_id=serializer.validated_data["vehicle"].id,
            requested_entry_date=serializer.validated_data["requested_entry_date"],
            membership_type=serializer.validated_data["membership_type"],
            created_by=self.request.user,
        )

        serializer.instance = membership_request

    # Pour la soumission de la requete. Lurl devra etre
    # POST /api/fleet/vehicle-membership-requests/<id>/submit/
    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        membership_request = self.get_object()

        submitted_request = submit_vehicle_membership_request(
        membership_request_id=membership_request.id,
        submitted_by=request.user,
        )
        serializer = self.get_serializer(submitted_request)
        return Response(serializer.data,status=status.HTTP_200_OK,)
    
  # Pour lannulation de la requete. Lurl devra etre
    # POST /api/fleet/vehicle-membership-requests/<id>/cancel/
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        membership_request = self.get_object()

        cancelled_request = cancel_vehicle_membership_request(
            membership_request_id=membership_request.id,
            cancelled_by=request.user,
        )

        serializer = self.get_serializer(cancelled_request)
        return Response(serializer.data,status=status.HTTP_200_OK,)
    

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        membership_request = self.get_object()

        approved_request = approve_vehicle_membership_request(
        membership_request_id=membership_request.id,
        approved_by=request.user,
        decision_comment=request.data.get("decision_comment"),
        )

        serializer = self.get_serializer(approved_request)

        return Response(serializer.data,status=status.HTTP_200_OK,)


    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        membership_request = self.get_object()

        rejected_request = reject_vehicle_membership_request(
        membership_request_id=membership_request.id,
        rejected_by=request.user,
        decision_comment=request.data.get("decision_comment"),
        )

        serializer = self.get_serializer(rejected_request)
        return Response(serializer.data,status=status.HTTP_200_OK,)
 

class VehicleDocumentViewSet(AuditUserMixin,SoftDeleteMixin,ModelViewSet,):
    queryset = VehicleDocument.objects.filter(is_deleted=False)
    serializer_class = VehicleDocumentSerializer
    permission_classes=[VehiclePermission]
