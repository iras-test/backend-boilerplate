from django.contrib.auth.models import AbstractUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView

from backend_boilerplate.utils.constants import (
    CAN_SPECIAL_EDIT,
)
import logging

logger = logging.getLogger(__name__)


class CustomPermissions(IsAuthenticated):
    def has_permission(self, request: Request, view: APIView) -> bool:
        user: AbstractUser = getattr(request, "user")
        is_authenticated = super().has_permission(request, view)
        
        if not is_authenticated:
            return False
        
        fields_requiring_special_permission = ["status"]
        
        if getattr(view, "action") in ["update", "partial_update"]:
            for field in fields_requiring_special_permission:
                if field in request.data.keys():
                    if not self.user_has_group_permission(user, CAN_SPECIAL_EDIT[0]):
                        return False
            return True
        
        return True
    
    def user_has_group_permission(self, user: AbstractUser, perm_codename: str) -> bool:
        for group in user.groups.all():
            if group.permissions.filter(codename=perm_codename).exists():
                return True
        return False
