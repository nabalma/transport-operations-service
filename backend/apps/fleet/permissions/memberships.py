from apps.fleet.permissions import BaseGroupPermission
from rest_framework.permissions import SAFE_METHODS
from apps.fleet.constants import UserGroup

# -- VehicleMembershipPermission
class VehicleMembershipPermission(BaseGroupPermission):

    def _get_allowed_groups(self, request):
        if request.method in SAFE_METHODS:
            return [
                UserGroup.MANAGER,
                UserGroup.SUPERVISOR,
                UserGroup.INSPECTOR,
                UserGroup.FLEET_MANAGER,
            ]

        return [
            UserGroup.MANAGER,
        ]

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        allowed_groups = self._get_allowed_groups(request)

        return self._has_any_group(request,allowed_groups,)
    

# -- VehicleMembershipRequestPermission
class VehicleMembershipRequestPermission(BaseGroupPermission):

    def _get_allowed_groups(self, request, view):
        if view.action == "create":
            return [UserGroup.SUPERVISOR]

        if view.action in ["approve", "reject"]:
            return [UserGroup.MANAGER]

        return [UserGroup.MANAGER,UserGroup.SUPERVISOR,]

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        allowed_groups = self._get_allowed_groups(request, view)

        return self._has_any_group(request,allowed_groups,)

    def has_object_permission(self, request, view, obj):
        if view.action == "cancel":
            return obj.created_by == request.user

        return True
    
