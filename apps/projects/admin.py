from django.contrib import admin
from taggit.models import Tag

from .models import Project


class TagListFilter(admin.SimpleListFilter):
    title = "tag"
    parameter_name = "tag"

    def lookups(self, request, model_admin):
        return [(tag.slug, tag.name) for tag in Tag.objects.order_by("name")]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(tags__slug=self.value())
        return queryset


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "published_at", "updated_at")
    list_filter = ("status", "published_at", TagListFilter)
    search_fields = ("title", "short_description")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    list_editable = ("status",)
