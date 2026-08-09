# -- BaseGroupPermission
from rest_framework.permissions import BasePermission, SAFE_METHODS



class BaseGroupPermission(BasePermission):

    def _has_any_group(self, request, allowed_groups):
        return request.user.groups.filter(name__in=allowed_groups).exists()
