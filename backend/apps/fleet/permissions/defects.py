
from apps.fleet.permissions import BaseGroupPermission
from rest_framework.permissions import SAFE_METHODS
from apps.fleet.constants import UserGroup


# -- SubmitDefectReleaseRequestPermission
class SubmitDefectReleaseRequestPermission(BaseGroupPermission):

    def _get_allowed_groups(self, request):
        if request.method in SAFE_METHODS:
            return [
                UserGroup.MANAGER,
                UserGroup.SUPERVISOR,
                UserGroup.INSPECTOR,
                UserGroup.FLEET_MANAGER,
            ]

        return [
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


# -- GenerateWorkOrderPermission
class GenerateWorkOrderPermission(BaseGroupPermission):

    def _get_allowed_groups(self, request):
        if request.method in SAFE_METHODS:
            return [
                UserGroup.MANAGER,
                UserGroup.SUPERVISOR,
                UserGroup.INSPECTOR,
                UserGroup.FLEET_MANAGER,
            ]

        return [
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



class ValidateDefectReleaseRequestPermission(BaseGroupPermission):

    def _get_allowed_groups(self, request):
        if request.method in SAFE_METHODS:
            return [
                UserGroup.MANAGER,
                UserGroup.SUPERVISOR,
                UserGroup.INSPECTOR,
                UserGroup.FLEET_MANAGER,
            ]

        return [
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


class DefectReleaseRequestPermission(BaseGroupPermission):

    def _get_allowed_groups(self, request):
        if request.method in SAFE_METHODS:
            return [
                UserGroup.MANAGER,
                UserGroup.SUPERVISOR,
                UserGroup.INSPECTOR,
                UserGroup.FLEET_MANAGER,
            ]

        return [
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
