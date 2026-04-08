from backend_boilerplate.utils.models import BaseModel
from django.db import models

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
    
class Region(AbstractConfigurableModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        abstract = True

class District(AbstractConfigurableModel):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="districts"
    )

    class Meta:
        abstract = True


class County(AbstractConfigurableModel):
    parent = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="counties"
    )

    class Meta:
        abstract = True


class SubCounty(AbstractConfigurableModel):
    parent = models.ForeignKey(
        County, on_delete=models.CASCADE, related_name="subcounties"
    )

    class Meta:
        abstract = True


class Parish(AbstractConfigurableModel):
    parent = models.ForeignKey(
        SubCounty, on_delete=models.CASCADE, related_name="parishes"
    )

    class Meta:
        abstract = True


class Village(AbstractConfigurableModel):
    parent = models.ForeignKey(
        Parish, on_delete=models.CASCADE, related_name="villages"
    )

    class Meta:
        abstract = True


class Street(AbstractConfigurableModel):
    parent = models.ForeignKey(
        Village, on_delete=models.CASCADE, related_name="streets"
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
        Region,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    district = models.ForeignKey(
        District,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    county = models.ForeignKey(
        County,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    sub_county = models.ForeignKey(
        SubCounty,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    parish = models.ForeignKey(
        Parish,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    village = models.ForeignKey(
        Village,
        models.DO_NOTHING,
        null=True,
        blank=True,
    )
    street = models.ForeignKey(
        Street,
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