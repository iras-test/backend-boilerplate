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
    
class RegionModel(AbstractConfigurableModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        abstract = True

class DistrictModel(AbstractConfigurableModel):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        RegionModel, on_delete=models.CASCADE, related_name="districts"
    )

    class Meta:
        abstract = True


class CountyModel(AbstractConfigurableModel):
    parent = models.ForeignKey(
        DistrictModel, on_delete=models.CASCADE, related_name="counties"
    )

    class Meta:
        abstract = True


class SubCountyModel(AbstractConfigurableModel):
    parent = models.ForeignKey(
        CountyModel, on_delete=models.CASCADE, related_name="subcounties"
    )

    class Meta:
        abstract = True


class ParishModel(AbstractConfigurableModel):
    parent = models.ForeignKey(
        SubCountyModel, on_delete=models.CASCADE, related_name="parishes"
    )

    class Meta:
        abstract = True


class VillageModel(AbstractConfigurableModel):
    parent = models.ForeignKey(
        ParishModel, on_delete=models.CASCADE, related_name="villages"
    )

    class Meta:
        abstract = True


class StreetModel(AbstractConfigurableModel):
    parent = models.ForeignKey(
        VillageModel, on_delete=models.CASCADE, related_name="streets"
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
        RegionModel,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    district = models.ForeignKey(
        DistrictModel,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    county = models.ForeignKey(
        CountyModel,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    sub_county = models.ForeignKey(
        SubCountyModel,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    parish = models.ForeignKey(
        ParishModel,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    village = models.ForeignKey(
        VillageModel,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    street = models.ForeignKey(
        StreetModel,
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

class Configuration(AbstractConfigurableModel):
    key = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        abstract = True
        unique_together = ("key", "name")


class NotificationRecipientGroups(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="recipients_groups"
    )

    class Meta:
        abstract = True


class NotificationSettings(BaseModel):
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
        NotificationRecipientGroups,
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