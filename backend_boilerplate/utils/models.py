import uuid
from typing import Any

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        get_user_model(),
        models.DO_NOTHING,
        related_name="%(app_label)s_%(class)s_updated_by",
        db_column="updated_by",
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        get_user_model(),
        models.DO_NOTHING,
        related_name="%(app_label)s_%(class)s_created_by",
        db_column="created_by",
    )
    deleted = models.BooleanField(default=False)

    action_comment = None
    author = None
    supporting_documents = None

    author = None

    class Meta:
        abstract = True
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        updated_by = kwargs.pop("updated_by", None)
        if updated_by:
            self.updated_by = updated_by
        self.updated_at = timezone.now()
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            update_fields = list(update_fields)
            if "updated_by" not in update_fields:
                update_fields.append("updated_by")
            kwargs["update_fields"] = update_fields
        return super().save(*args, **kwargs)

    def delete(
        self, using: Any = None, keep_parents: bool = False
    ) -> tuple[int, dict[str, int]]:
        self.deleted = True
        update_fields = ["deleted"]

        self.save(update_fields=update_fields)
        return (0, {})
