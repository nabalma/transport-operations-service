from apps.fleet.permissions import BaseGroupPermission
from rest_framework.permissions import SAFE_METHODS
from apps.fleet.constants import UserGroup



# -- VehiclePermission
class VehiclePermission(BaseGroupPermission):

    def _get_allowed_groups(self, request):
        if request.method in SAFE_METHODS:
            return [
                UserGroup.SUPERVISOR,
                UserGroup.MANAGER,
                UserGroup.INSPECTOR,
                UserGroup.FLEET_MANAGER,
            ]

        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [
                UserGroup.SUPERVISOR,
            ]

        return []

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        allowed_groups = self._get_allowed_groups(request)

        return self._has_any_group(request,allowed_groups,)



# -- VehicleAgePolicyConfigurationPermission
class VehicleAgePolicyConfigurationPermission(BaseGroupPermission):

    def _get_allowed_groups(self, request):
        if request.method in SAFE_METHODS:
            return [
                UserGroup.MANAGER,
                UserGroup.SUPERVISOR,
                UserGroup.FLEET_MANAGER
            ]

        return [
            UserGroup.MANAGER,
        ]

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        allowed_groups = self._get_allowed_groups(
            request,
        )

        return self._has_any_group(request,allowed_groups,)





    
