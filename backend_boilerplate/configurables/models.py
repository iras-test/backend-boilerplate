from backend_boilerplate.utils.constants import NOTIFICATION_CHANNEL_CHOICES
from backend_boilerplate.utils.models import BaseModel
from django.db import models
from django.conf import settings


ACTIVE_LOCATION = "active"
INACTIVE_LOCATION = "inactive"

LOCATION_CHOICES = (
    (ACTIVE_LOCATION, "Active"),
    (INACTIVE_LOCATION, "Inactive"),
)

class AbstractConfigurableModel(BaseModel):
    """
    Abstract base model for configurable entities.
    This contains the common attributes and methods for all entities.
    """

    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=LOCATION_CHOICES, default="active")

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
    
class AbstractRegion(AbstractConfigurableModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        abstract = True

class AbstractDistrict(AbstractConfigurableModel):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        AbstractRegion, on_delete=models.CASCADE, related_name="districts"
    )

    class Meta:
        abstract = True


class AbstractCounty(AbstractConfigurableModel):
    parent = models.ForeignKey(
        AbstractDistrict, on_delete=models.CASCADE, related_name="counties"
    )

    class Meta:
        abstract = True


class AbstractSubCounty(AbstractConfigurableModel):
    parent = models.ForeignKey(
        AbstractCounty, on_delete=models.CASCADE, related_name="subcounties"
    )

    class Meta:
        abstract = True


class AbstractParish(AbstractConfigurableModel):
    parent = models.ForeignKey(
        AbstractSubCounty, on_delete=models.CASCADE, related_name="parishes"
    )

    class Meta:
        abstract = True


class AbstractVillage(AbstractConfigurableModel):
    parent = models.ForeignKey(
        AbstractParish, on_delete=models.CASCADE, related_name="villages"
    )

    class Meta:
        abstract = True


class AbstractStreet(AbstractConfigurableModel):
    parent = models.ForeignKey(
        AbstractVillage, on_delete=models.CASCADE, related_name="streets"
    )

    class Meta:
        abstract = True

class BaseLocationModel(BaseModel):
    """
    Abstract base model for storing hierarchical location references.

    Use this model for entities that map to any subset of the location hierarchy
    (region, district, county, sub-county, parish, village, and street). Any
    unused hierarchy fields can be left null.
    """
    region = models.ForeignKey(
        AbstractRegion,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    district = models.ForeignKey(
        AbstractDistrict,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    county = models.ForeignKey(
        AbstractCounty,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    sub_county = models.ForeignKey(
        AbstractSubCounty,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    parish = models.ForeignKey(
        AbstractParish,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    village = models.ForeignKey(
        AbstractVillage,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    street = models.ForeignKey(
        AbstractStreet,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        max_digits=25, decimal_places=20, null=True, blank=True
    )
    latitude = models.DecimalField(
        max_digits=25, decimal_places=20, null=True, blank=True
    )

    class Meta:
        abstract = True

class AbstractConfiguration(AbstractConfigurableModel):
    key = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        abstract = True
        unique_together = ("key", "name")


class AbstractNotificationRecipientGroups(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="recipients_groups"
    )

    class Meta:
        abstract = True


class AbstractNotificationSettings(BaseModel):
    notification_name = models.CharField(
        max_length=200, unique=True, null=False, blank=False
    )
    subject = models.CharField(max_length=200, null=True, blank=True)
    body = models.JSONField()
    notification_type = models.CharField(
        max_length=50, choices=NOTIFICATION_CHANNEL_CHOICES
    )
    trigger_event = models.CharField(max_length=100, null=True, blank=True)
    recipients = models.ForeignKey(
        AbstractNotificationRecipientGroups,
        related_name="recipients_groups",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    enabled = models.BooleanField(default=True)
    effective_start_date = models.DateField(null=True, blank=True)
    effective_end_date = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True