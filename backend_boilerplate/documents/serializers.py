from django.core.files.storage import default_storage
from rest_framework import serializers
from user_mgmt.serializers import SimplestUserSerializer
from utils.serializers import (
    ActivityModelSerializer,
    CreateOnlyCurrentUserDefault,
)

class AbstractDocumentSerializer(serializers.ModelSerializer):
    created_by = SimplestUserSerializer(
        required=False, default=CreateOnlyCurrentUserDefault()
    )
    class Meta:
        exclude = ("object_id", "content_type")
    # file = serializers.SerializerMethodField()

    # def get_file(self, obj):
    #     url = default_storage.url(obj.file.name)
    #     media_index = url.find("/media")
    #     return url.replace(url[:media_index], "") if url.find("/media") != -1 else url


class AbstractSimplestDocumentSerializer(serializers.ModelSerializer):
    created_by = SimplestUserSerializer(
        required=False, default=CreateOnlyCurrentUserDefault()
    )

    # file = serializers.SerializerMethodField()

    # def get_file(self, obj):
    #     url = default_storage.url(obj.file.name)
    #     if url.startswith("/media"):
    #         return url[len("/media"):]
    #     return url

    class Meta:
        exclude = ("object_id", "content_type")
        extra_kwargs = {"reference_number": {"read_only": True}}


class AbstractSimpleDocumentSerializer(ActivityModelSerializer):
    created_by = SimplestUserSerializer(
        required=False, default=CreateOnlyCurrentUserDefault()
    )

    file = serializers.SerializerMethodField()

    def get_file(self, obj):
        url = default_storage.url(obj.file.name)
        if url.startswith("/media"):
            return url[len("/media") :]
        return url

    class Meta:
        exclude = ("object_id", "content_type")
        # fields = "__all__"

class AbstractSimplerDocumentSerializer(ActivityModelSerializer):
    created_by = SimplestUserSerializer(
        required=False, default=CreateOnlyCurrentUserDefault()
    )

    class Meta:
        fields = "__all__"


class AbstractAttachmentDetailSerializer(serializers.Serializer):
    serializer_class = None
    allow_many = True

    def to_representation(self, instance):
        json = dict()
        for category in instance:
            json[category] = (
                self.serializer_class(
                    instance=instance[category], many=self.allow_many
                ).data
                if instance[category]
                else None
            )
        return json

class AbstractDocumentDetailSerializer(AttachmentDetailSerializer):
    serializer_class = SimpleDocumentSerializer