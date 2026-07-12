from rest_framework.permissions import BasePermission, SAFE_METHODS


# -- InspectionPermission
class InspectionPermission(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return request.user.groups.filter(
                name__in=["Inspector", "Supervisor", "Fleet Manager"]
            ).exists()

        if request.method == "POST":
            return request.user.groups.filter(
                name__in=["Inspector", "Supervisor"]
            ).exists()

        if request.method in ["PUT", "PATCH", "DELETE"]:
            return request.user.groups.filter(
                name="Inspector"
            ).exists()

        return False
    

# -- InspectionConfigurationPermission
class InspectionConfigurationPermission(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return request.user.groups.filter(
                name__in=["Supervisor", "Inspector", "Fleet Manager"]
            ).exists()

        return request.user.groups.filter(
            name="Supervisor"
        ).exists()