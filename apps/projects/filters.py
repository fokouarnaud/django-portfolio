import django_filters
from django.db.models import Q

from .models import Project


class ProjectFilter(django_filters.FilterSet):
    tag = django_filters.CharFilter(field_name="tags__slug", lookup_expr="exact")
    year = django_filters.NumberFilter(field_name="published_at", lookup_expr="year")
    q = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Project
        fields = ["tag", "year", "q"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value)
            | Q(short_description__icontains=value)
            | Q(tags__name__icontains=value)
        ).distinct()
