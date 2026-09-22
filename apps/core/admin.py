from django.contrib import admin
from django.shortcuts import redirect

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Apparence", {"fields": ("font_theme", "color_theme")}),
        (
            "Contact & réseaux",
            {
                "fields": (
                    "whatsapp_number",
                    "youtube_url",
                    "facebook_url",
                    "demo_url",
                    "presentation_video_url",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        settings_obj = SiteSettings.get_solo()
        return redirect("admin:core_sitesettings_change", settings_obj.pk)
