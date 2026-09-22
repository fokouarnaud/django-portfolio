from django.contrib import admin
from django.shortcuts import redirect
from django.utils.html import format_html

from .models import SiteSettings

_ALL_GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Libre+Bodoni:wght@600&family=Public+Sans:wght@400"
    "&family=Inter:wght@400;600"
    "&family=Playfair+Display:wght@600&family=Source+Sans+3:wght@400"
    "&display=swap"
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    readonly_fields = ("font_preview", "color_preview")

    fieldsets = (
        (
            "Apparence",
            {"fields": ("font_theme", "font_preview", "color_theme", "color_preview")},
        ),
        (
            "Contact & réseaux",
            {
                "fields": (
                    "whatsapp_number",
                    "youtube_url",
                    "facebook_url",
                    "demo_url",
                    "presentation_video_url",
                ),
                "classes": ("collapse",),
                "description": "Affichés en pied de page du site uniquement s'ils sont renseignés.",
            },
        ),
    )

    class Media:
        css = {"all": (_ALL_GOOGLE_FONTS_URL,)}

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        settings_obj = SiteSettings.get_solo()
        return redirect("admin:core_sitesettings_change", settings_obj.pk)

    @admin.display(description="Aperçu de la police")
    def font_preview(self, obj):
        return format_html(
            '<span style="font-family:{}; font-size:1.5rem;">'
            "Aa Bb Cc — Exemple de titre</span>",
            obj.font_preview_family,
        )

    @admin.display(description="Aperçu du thème")
    def color_preview(self, obj):
        swatch = obj.color_preview_swatch
        return format_html(
            '<span style="display:inline-flex;align-items:center;gap:8px;'
            'padding:10px 14px;border-radius:6px;border:1px solid #d1d5db;'
            'background:{bg};color:{fg};">Exemple de texte</span>',
            bg=swatch["background"],
            fg=swatch["foreground"],
        )
