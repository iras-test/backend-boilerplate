from django.contrib.contenttypes.models import ContentType
from .serializers import SimplerDocumentSerializer

def save_attachments(data, instance, model, context, replace=False):
    if data is not None:
        for attachment in data:
            content_type = ContentType.objects.get_for_model(model)

            attachment.pop("created_by", getattr(context.get("request"), "user"))
            attachment_data = {
                **attachment,
                "content_type": content_type.id,
                "object_id": instance.id,
            }

            if replace and attachment_data.get("caption"):
                instance.attachments.filter(
                    caption=attachment_data.get("caption")
                ).delete()

            attachment = SimplerDocumentSerializer(
                data=attachment_data, context=context
            )
            attachment.is_valid(raise_exception=True)
            attachment.save()