from django.db import models
from django.contrib.auth.models import AbstractUser


class AbstractUserMixin(AbstractUser):
    """
    Projects inherit like this:
        class User(AbstractUserMixin):
            id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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

