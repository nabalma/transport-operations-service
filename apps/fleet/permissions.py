from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.fleet.constants import UserGroup


# -- BaseGroupPermission
class BaseGroupPermission(BasePermission):

    def _has_any_group(self, request, allowed_groups):
        return request.user.groups.filter(name__in=allowed_groups).exists()


#=======================================
# PERMISSIONS
#=======================================
# -- InspectionPermission
class InspectionPermission(BaseGroupPermission):

    def _get_allowed_groups(self, request):
        if request.method in SAFE_METHODS:
            return [UserGroup.INSPECTOR,UserGroup.SUPERVISOR,UserGroup.FLEET_MANAGER,]

        if request.method == "POST":
            return [UserGroup.INSPECTOR,UserGroup.SUPERVISOR,]

        if request.method in ["PUT", "PATCH", "DELETE"]:
            return [UserGroup.INSPECTOR,]

        return []

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        allowed_groups = self._get_allowed_groups(request)
        return self._has_any_group(request,allowed_groups,)


# -- InspectionConfigurationPermission
class InspectionConfigurationPermission(BaseGroupPermission):

    def _get_allowed_groups(self, request):
        if request.method in SAFE_METHODS:
            return [UserGroup.INSPECTOR,UserGroup.SUPERVISOR,UserGroup.FLEET_MANAGER,]

        return [UserGroup.SUPERVISOR,]

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        allowed_groups = self._get_allowed_groups(request)
        return self._has_any_group(request,allowed_groups,)
    

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
    
# -- FleetMembershipPermission
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
    

# -- FleetMembershipPermission
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

        return self._has_any_group(
            request,
            allowed_groups,
        )