from rest_framework.viewsets import ModelViewSet
from django.db.models import ManyToManyField
from django.db.models.fields.related import ForeignObjectRel
from backend_boilerplate.user_mgmt.permissions import CustomPermissions
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.fields import GenericRelation

class BaseViewSet(ModelViewSet):
    permission_classes = (CustomPermissions,)
    filter_backends = (DjangoFilterBackend,)

    def update(self, request, *args, **kwargs):
        body = request.data

        instance = self.get_object()
        old_instance = self.get_object()

        model_fields = [
            field.name
            for field in instance._meta.get_fields()
            if not isinstance(field, ManyToManyField)
               and not isinstance(field, GenericRelation)
               and not isinstance(field, ForeignObjectRel)
        ]
        update_fields = list(set(model_fields) & set(body.keys()))

        response = super().update(request, *args, **kwargs)

        instance = self.get_object()

        instance._old_instance = old_instance

        extra_fields = []
        if "author" in model_fields:
            setattr(instance, "author", request.user)
            extra_fields.append("author")
        if "action_comment" in model_fields:
            setattr(instance, "action_comment", request.data.get("action_comment"))
            extra_fields.append("action_comment")

        docs = request.FILES.getlist("supporting_documents")
        supporting_documents = [
            default_storage.save(f"support_docs/{file.name}", ContentFile(file.read()))
            for file in docs
        ]
        if "supporting_documents" in model_fields:
            setattr(instance, "supporting_documents", supporting_documents)
            extra_fields.append("supporting_documents")

        save_fields = list(set(update_fields) | set(extra_fields))
        if save_fields:
            instance.save(update_fields=save_fields, updated_by=request.user)

        return response

