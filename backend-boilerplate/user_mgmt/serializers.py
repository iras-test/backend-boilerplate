from django.contrib.auth import authenticate, get_user_model
from rest_framework.serializers import (
    ModelSerializer,
)
class SimplestUserSerializer(ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "id",
        )
