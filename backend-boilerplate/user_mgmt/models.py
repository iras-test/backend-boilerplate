"""Abstract base models for user management."""

import uuid
from django.db import models
from backend_boilerplate.utils.models import BaseModel


class AbstractUserMixin(models.Model):
    """
    Abstract mixin providing ADDITIONAL user fields beyond Django's AbstractUser.
    
    Projects inherit like this:
        class User(AbstractUser, AbstractUserMixin):
            id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Override default int id
            objects = CustomUserManager()
            USERNAME_FIELD = 'phone_number'  # or 'email'
    """

    phone_number = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        null=True,
        blank=True,
        help_text="Optional phone number. Unique when provided."
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['phone_number']),
        ]


class AbstractUserProfile(BaseModel):
    """
    Abstract profile model with common identity location fields.
    
    Projects inherit and add a OneToOneField to their concrete User model:
        class UserProfile(AbstractUserProfile):
            user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
            # Project-specific fields (location, department, etc.)
    
    """
    
    nin = models.CharField(
        max_length=14,
        null=True,
        blank=True,
        unique=True,
        help_text="National ID Number (if applicable in your country)."
    )
    
    tin = models.CharField(
        max_length=14,
        null=True,
        blank=True,
        unique=True,
        help_text="Tax ID Number."
    )
    
    passport_number = models.CharField(
        max_length=14,
        null=True,
        blank=True,
        unique=True,
        help_text="Passport number for international identification."
    )
    
    physical_address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Physical address of the user."
    )

    class Meta(BaseModel.Meta):
        abstract = True
        indexes = BaseModel.Meta.indexes + [
            models.Index(fields=['nin']),
            models.Index(fields=['tin']),
            models.Index(fields=['passport_number']),
        ]
