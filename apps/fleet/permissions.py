from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.fleet.constants import UserGroup


# -- InspectionPermission
class InspectionPermission(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return request.user.groups.filter(
                name__in=[UserGroup.INSPECTOR, UserGroup.SUPERVISOR, UserGroup.FLEET_MANAGER]
            ).exists()

        if request.method == "POST":
            return request.user.groups.filter(
                name__in=[UserGroup.INSPECTOR, UserGroup.SUPERVISOR]
            ).exists()

        if request.method in ["PUT", "PATCH", "DELETE"]:
            return request.user.groups.filter(
                name=UserGroup.INSPECTOR,
            ).exists()

        return False
    

# -- InspectionConfigurationPermission
class InspectionConfigurationPermission(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return request.user.groups.filter(
                 name__in=[UserGroup.INSPECTOR, UserGroup.SUPERVISOR, UserGroup.FLEET_MANAGER]
            ).exists()

        return request.user.groups.filter(
            name=UserGroup.SUPERVISOR
        ).exists()