from backend_boilerplate.utils.filters import GenericDateFilterSet
from django_filters import CharFilter


class AbstractConfigurableFilter(GenericDateFilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains", label="Name")
    status = CharFilter(field_name="status", lookup_expr="iexact", label="Status")


class RegionModelFilterSet(AbstractConfigurableFilter):
    """Reusable filters for top-level locations without a parent relation."""

class DistrictModelFilterSet(AbstractConfigurableFilter):
    region_name = CharFilter(field_name="parent__name", lookup_expr="icontains")


class CountyModelFilterSet(AbstractConfigurableFilter):
    district_name = CharFilter(field_name="parent__name", lookup_expr="icontains")

class SubCountyModelFilterSet(AbstractConfigurableFilter):
    county_name = CharFilter(field_name="parent__name", lookup_expr="icontains")


class ParishModelFilterSet(AbstractConfigurableFilter):
    subcounty_name = CharFilter(field_name="parent__name", lookup_expr="icontains")


class VillageModelFilterSet(AbstractConfigurableFilter):
    parish_name = CharFilter(field_name="parent__name", lookup_expr="icontains")


class StreetModelFilterSet(AbstractConfigurableFilter):
    village_name = CharFilter(field_name="parent__name", lookup_expr="icontains")

class BaseLocationModelFilterSet(GenericDateFilterSet):
    region = CharFilter(field_name="region__name", lookup_expr="iexact", label="Region")
    district = CharFilter(field_name="district__name", lookup_expr="iexact")
    parish = CharFilter(field_name="parish__name", lookup_expr="iexact")
    county = CharFilter(field_name="county__name", lookup_expr="iexact")
    subcounty = CharFilter(field_name="subcounty__name", lookup_expr="iexact")
    village = CharFilter(field_name="village__name", lookup_expr="iexact")
    street = CharFilter(field_name="street__name", lookup_expr="iexact")
    longitude = CharFilter(field_name="longitude", lookup_expr="icontains")
    latitude = CharFilter(field_name="latitude", lookup_expr="icontains")

class ConfigurationModelFilterSet(AbstractConfigurableFilter):
    """Reusable filters for all configurable models."""