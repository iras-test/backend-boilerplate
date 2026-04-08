from collections import OrderedDict
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from rest_framework.fields import SkipField
from .helpers import get_external_user, post_nested_save
from generic_relations.relations import GenericRelatedField
from actstream.models import Action



from .constants import ALLOWED_FILE_EXTENSIONS

class CreateOnlyCurrentUserDefault(serializers.CurrentUserDefault):

    def set_context(self, serializer_field):
        self.is_update = bool(
            getattr(serializer_field, "parent", None)
            and getattr(serializer_field.parent, "instance", None) is not None
        )

    def __call__(self, serializer_field):
        # Ensure set_context is invoked — DRF doesn't always call set_context on default objects.
        try:
            self.set_context(serializer_field)
        except Exception:
            # Fallback: compute is_update directly if set_context cannot run for any reason.
            self.is_update = bool(
                getattr(serializer_field, "parent", None)
                and getattr(serializer_field.parent, "instance", None) is not None
            )

        if getattr(self, "is_update", False):
            # TODO: Make sure this check is sufficient for all update scenarios
            raise SkipField()
        user = super(CreateOnlyCurrentUserDefault, self).__call__(serializer_field)
        if user and getattr(user, "is_authenticated", False):
            return user
        return get_external_user()

class CustomGenericRelatedField(GenericRelatedField):
    def get_serializer_for_instance(self, instance):
        for klass in instance.__class__.mro():
            if klass in self.serializers:
                return self.serializers[klass]
    
        raise serializers.ValidationError(
            instance.__class__
        )

class ActivityModelSerializer(serializers.ModelSerializer):
    action_comment = serializers.CharField(required=False, write_only=True)
    supporting_documents = serializers.ListField(
        child=serializers.FileField(
            required=False, validators=[FileExtensionValidator(ALLOWED_FILE_EXTENSIONS)]
        ),
        allow_empty=True,
        required=False,
        write_only=True,
    )

    def validate(self, attrs):
        if self.instance and self.context.get("request"):
            attrs["author"] = getattr(self.context.get("request", None), "user")

        docs = attrs.get("supporting_documents")

        if docs:

            attrs["supporting_documents"] = [
                default_storage.save(
                    f"support_docs/{file.name}", ContentFile(file.read())
                )
                for file in docs
            ]

        return super().validate(attrs)

    class Meta:
        model = Action
        fields = "__all__"


class NestedModelSerializer(serializers.ModelSerializer):

    @transaction.atomic
    def create(self, validated_data):
        return self.nested_save_override(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        return self.nested_save_override(validated_data, instance=instance)

    def nested_save_override(self, validated_data, instance=None):
        nested_method_models = []
        nested_data = []

        field_source_map = dict()
        for field_key in self.get_fields():
            field_value = self.get_fields().get(field_key, None)
            if field_value:
                source = getattr(field_value, "source", None)
                readOnly = getattr(field_value, "read_only", False)
                if source and not readOnly:
                    field_source_map[source] = field_key

        for attribute_key in self.validated_data.keys():
            clean_attribute_key = field_source_map.get(attribute_key, attribute_key)
            save_method = getattr(
                self, "save_nested_{}".format(clean_attribute_key), None
            )
            attribute_value = self.validated_data.get(attribute_key, None)
            if save_method:
                # Filter nested save model data
                if attribute_value:
                    nested_method_models.append((save_method, attribute_value))

                # remove attribute from validated data if it exists
                validated_data.pop(attribute_key)
            elif type(attribute_value) in [dict, list]:
                # Filter nested data
                serializer_field = self.get_fields().get(clean_attribute_key, None)
                if serializer_field:
                    serializer_field_child = getattr(serializer_field, "child", None)

                    if serializer_field_child:
                        serializer_class = serializer_field_child.__class__
                    else:
                        serializer_class = serializer_field.__class__

                    if serializer_class and issubclass(
                        serializer_class, serializers.Serializer
                    ):
                        fk_keys = []
                        if (
                            serializer_class.Meta
                            and serializer_class.Meta.model
                            and self.Meta
                            and self.Meta.model
                        ):
                            for (
                                model_field
                            ) in serializer_class.Meta.model._meta.get_fields():
                                if model_field.related_model == self.Meta.model:
                                    fk_keys.append(model_field.name)
                        if isinstance(attribute_value, list):
                            for single_attribute_value in attribute_value:
                                nested_data.append(
                                    (
                                        clean_attribute_key,
                                        single_attribute_value,
                                        serializer_class,
                                        fk_keys,
                                    )
                                )
                        else:
                            nested_data.append(
                                (
                                    clean_attribute_key,
                                    attribute_value,
                                    serializer_class,
                                    fk_keys,
                                )
                            )
                    else:
                        continue

                # remove attribute from validated data to prevent writable
                # nested non readonly fields error
                validated_data.pop(attribute_key)

            if type(attribute_value) in [dict, OrderedDict]:
                attribute_value_object_id = attribute_value.get("id", None)
                if attribute_value_object_id:
                    serializer_field = self.get_fields().get(clean_attribute_key, None)
                    serializer_class = serializer_field.__class__
                    validated_data[clean_attribute_key] = (
                        serializer_class.Meta.model.objects.get(
                            pk=attribute_value_object_id
                        )
                    )

        is_created = not bool(instance)
        if instance:
            instance = super(NestedModelSerializer, self).update(
                instance, validated_data
            )
        else:
            instance = super(NestedModelSerializer, self).create(validated_data)

        try:
            # Saving nested values is best effort
            for attribute_details in nested_method_models:
                save_method = attribute_details[0]
                attribute_value = attribute_details[1]
                if save_method and attribute_value:
                    save_method(attribute_value, instance, created=is_created)

            for k, v, s, r in nested_data:
                v = dict(v)
                if r:
                    for related_key in r:
                        v[related_key] = instance
                if s.Meta.model:
                    if "id" in v:
                        s.Meta.model.objects.update_or_create(id=v["id"], defaults=v)
                    else:
                        s.Meta.model.objects.create(**v)
                else:
                    serializer = s(data=v, **dict(context=self.context))
                    serializer.save()
        except Exception as e:
            raise e

        post_nested_save.send(
            sender=self.__class__.Meta.model, instance=instance, created=is_created
        )
        return instance

class SimpleUserSerializer(serializers.ModelSerializer):

    class Meta:
        ref_name = "utils-simple-user-serialzer"
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "email",
        )

class SimplerUserSerializer(serializers.ModelSerializer):

    class Meta:
        ref_name = "utils-simple-user-serialzer"
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "id",
        )

# Serializer to help with uploading mob files that are CSVs
class BulkUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, file):
        if not file.name.lower().endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed.")

        # Future validations can be "file_size"

        return file

