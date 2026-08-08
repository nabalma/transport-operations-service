from apps.fleet.permissions import BaseGroupPermission
from rest_framework.permissions import SAFE_METHODS
from apps.fleet.constants import UserGroup


class VehicleAvailabilityEvaluationPermission(BaseGroupPermission):

    def _get_allowed_groups(self, request):
        if request.method in SAFE_METHODS:
            return [
                UserGroup.SUPERVISOR,
                UserGroup.MANAGER,
                UserGroup.FLEET_MANAGER,
                UserGroup.INSPECTOR,
            ]

        return [
            UserGroup.SUPERVISOR,
             UserGroup.FLEET_MANAGER,
        ]


    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        allowed_groups = self._get_allowed_groups(request)

        return self._has_any_group(
            request,
            allowed_groups,
        )






class VehicleAvailabilityEvaluationReasonPermission(BaseGroupPermission):

    def _get_allowed_groups(self, request):
        if request.method in SAFE_METHODS:
            return [
                UserGroup.SUPERVISOR,
                UserGroup.MANAGER,
                UserGroup.FLEET_MANAGER,
                UserGroup.INSPECTOR,
            ]

        return [
            UserGroup.FLEET_MANAGER,
            UserGroup.INSPECTOR,
        ]


    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        allowed_groups = self._get_allowed_groups(request)

        return self._has_any_group(
            request,
            allowed_groups,
        )
