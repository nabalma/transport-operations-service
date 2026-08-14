
from apps.fleet.permissions import BaseGroupPermission
from rest_framework.permissions import SAFE_METHODS
from apps.fleet.constants import DefectCreationSource, UserGroup


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
                UserGroup.SUPERVISOR,
        ]

        return []

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        allowed_groups = self._get_allowed_groups(request)

        return self._has_any_group(
            request,
            allowed_groups,
        )

    def has_object_permission(
        self,
        request,
        view,
        release_request,
    ):
        defect = release_request.defect

        # Le défaut vient d’une inspection :
        # seul un inspecteur peut valider.
        if defect.source_inspection_id is not None:
            return self._has_any_group(
                request,
                [
                    UserGroup.INSPECTOR,
                ],
            )

        # Le défaut a été créé manuellement par le Fleet Manager :
        # seul un superviseur peut valider.
        if defect.creation_source == DefectCreationSource.USER:
            return self._has_any_group(
                request,
                [
                    UserGroup.SUPERVISOR,
                ],
            )

        return False


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
    



# -- DefectPermission
class DefectPermission(BaseGroupPermission):

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


