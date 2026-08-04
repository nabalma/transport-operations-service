
from django.conf import settings
from django.db import models

# -------------------------------------------------------------------
# 1-Base model
# Modèle abstrait commun pour created_at et updated_at.
# À hériter par les modèles qui doivent garder ces deux timestamps.
# -------------------------------------------------------------------
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    updated_at = models.DateTimeField(auto_now=True)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

   

    class Meta:
        abstract = True


# -------------------------------------------------------------------
# TimeStampedSoftDeletableModel
# Modèle abstrait ajoutant la suppression logique et sa traçabilité.
# -------------------------------------------------------------------
class TimeStampedSoftDeletableModel(TimeStampedModel):

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    deleted_reason = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True