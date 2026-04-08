from django_filters import FilterSet, IsoDateTimeFilter, CharFilter

class GenericDateFilterSet(FilterSet):
    created_at_min_date = IsoDateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_max_date = IsoDateTimeFilter(field_name="created_at", lookup_expr="lte")
    updated_at_min_date = IsoDateTimeFilter(field_name="updated_at", lookup_expr="gte")
    updated_at_max_date = IsoDateTimeFilter(field_name="updated_at", lookup_expr="lte")
    created_at = CharFilter(field_name='created_at', lookup_expr='icontains')