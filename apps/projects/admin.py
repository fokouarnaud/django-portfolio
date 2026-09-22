from django.contrib import admin
from django.utils.html import format_html
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
    list_display = ("cover_thumbnail", "title", "status", "published_at", "updated_at")
    list_display_links = ("title",)
    list_filter = ("status", "published_at", TagListFilter)
    search_fields = ("title", "short_description")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    list_editable = ("status",)
    readonly_fields = ("cover_preview", "created_at", "updated_at")

    fieldsets = (
        ("Contenu", {"fields": ("title", "slug", "short_description", "long_description")}),
        ("Média & liens", {"fields": ("cover_image", "cover_preview", "tags", "external_link")}),
        ("Publication", {"fields": ("status", "published_at", "created_at", "updated_at")}),
    )

    @admin.display(description="Aperçu")
    def cover_thumbnail(self, obj):
        if not obj.pk or not obj.cover_image:
            return "—"
        return format_html(
            '<img src="{}" alt="" style="width:48px;height:48px;object-fit:cover;'
            'border-radius:4px;">',
            obj.cover_image.url,
        )

    @admin.display(description="Aperçu de l'image")
    def cover_preview(self, obj):
        if not obj.pk or not obj.cover_image:
            return "L'aperçu apparaît une fois l'image enregistrée."
        return format_html(
            '<img src="{}" alt="" style="max-width:320px;max-height:200px;'
            'object-fit:cover;border-radius:8px;">',
            obj.cover_image.url,
        )
