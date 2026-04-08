from backend_boilerplate.utils.filters import GenericDateFilterSet
from django_filters import CharFilter


class AbstractConfigurableFilter(GenericDateFilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains", label="Name")
    status = CharFilter(field_name="status", lookup_expr="iexact", label="Status")


class RegionFilterSet(AbstractConfigurableFilter):
    """Reusable filters for top-level locations without a parent relation."""

class DistrictFilterSet(AbstractConfigurableFilter):
    region_name = CharFilter(field_name="parent__name", lookup_expr="icontains")


class CountyFilterSet(AbstractConfigurableFilter):
    district_name = CharFilter(field_name="parent__name", lookup_expr="icontains")

class SubCountyFilterSet(AbstractConfigurableFilter):
    county_name = CharFilter(field_name="parent__name", lookup_expr="icontains")


class ParishFilterSet(AbstractConfigurableFilter):
    subcounty_name = CharFilter(field_name="parent__name", lookup_expr="icontains")


class VillageFilterSet(AbstractConfigurableFilter):
    parish_name = CharFilter(field_name="parent__name", lookup_expr="icontains")


class StreetFilterSet(AbstractConfigurableFilter):
    village_name = CharFilter(field_name="parent__name", lookup_expr="icontains")

class BaseLocationFilterSet(GenericDateFilterSet):
    region = CharFilter(field_name="region__name", lookup_expr="iexact", label="Region")
    district = CharFilter(field_name="district__name", lookup_expr="iexact")
    parish = CharFilter(field_name="parish__name", lookup_expr="iexact")
    county = CharFilter(field_name="county__name", lookup_expr="iexact")
    subcounty = CharFilter(field_name="subcounty__name", lookup_expr="iexact")
    village = CharFilter(field_name="village__name", lookup_expr="iexact")
    street = CharFilter(field_name="street__name", lookup_expr="iexact")
    longitude = CharFilter(field_name="longitude", lookup_expr="icontains")
    latitude = CharFilter(field_name="latitude", lookup_expr="icontains")

class ConfigurationFilterSet(AbstractConfigurableFilter):
    """Reusable filters for all configurable models."""