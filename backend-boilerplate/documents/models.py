from django.utils import timezone
from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from utils.models import BaseModel
from .helpers import get_file_path
from utils.constants import DOCUMENT_TYPES, ALLOWED_FILE_EXTENSIONS

class Document(BaseModel):
    reference_number = models.CharField(max_length=50, null=True, blank=True)
    author_first_name = models.CharField(max_length=50, null=True, blank=True)
    author_last_name = models.CharField(max_length=50, null=True, blank=True)
    author_other_name = models.CharField(max_length=50, null=True, blank=True)
    author_phone_number = models.CharField(max_length=20, null=True, blank=True)
    author_email = models.EmailField(max_length=320, null=True, blank=True)
    physical_address = models.CharField(max_length=50, null=True, blank=True)

    document_type = models.CharField(max_length=100, choices=DOCUMENT_TYPES)
    caption = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    is_confidential = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    file = models.FileField(
        max_length=500,
        upload_to=get_file_path,
        validators=[FileExtensionValidator(ALLOWED_FILE_EXTENSIONS)],
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"{self.document_type} - {self.reference_number or self.pk}"

    class Meta(BaseModel.Meta):
        abstract = True
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["content_type"], name="document_content_type_idx"),
            models.Index(fields=["object_id"], name="document_object_id_idx"),
        ]
        ordering = ("-id",)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.reference_number:
            now = timezone.now()
            year = str(now.year)[-2:]
            timestamp = now.strftime("%m%d%H%M%S")

            pk_part = str(self.pk)[:8]

            self.reference_number = f"PD/DOC/{year}/{timestamp}{pk_part}"
            super().save(update_fields=["reference_number"])