from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response




# -------------------------------------------------------------------
# AuditUserMixin
# Renseigne automatiquement l'utilisateur qui crée ou modifie un objet.
# -------------------------------------------------------------------
class AuditUserMixin:

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user,
        )



# -------------------------------------------------------------------
# SoftDeleteMixin
# Remplace la suppression physique par une suppression logique.
# -------------------------------------------------------------------
class SoftDeleteMixin:

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.deleted_by = request.user

        deleted_reason = request.data.get("deleted_reason")

        if deleted_reason is not None:
            instance.deleted_reason = deleted_reason

        instance.save(
            update_fields=[
                "is_deleted",
                "deleted_at",
                "deleted_by",
                "deleted_reason",
                "updated_at",
            ]
        )

        return Response(status=status.HTTP_204_NO_CONTENT)