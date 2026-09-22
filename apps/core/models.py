import re

from django.core.validators import RegexValidator
from django.db import models

from .utils import youtube_embed_url

_GOOGLE_FONTS_URLS = {
    "editorial": (
        "https://fonts.googleapis.com/css2?"
        "family=Libre+Bodoni:wght@400;500;600;700"
        "&family=Public+Sans:wght@300;400;500;600;700&display=swap"
    ),
    "modern": (
        "https://fonts.googleapis.com/css2?"
        "family=Inter:wght@300;400;500;600;700;800&display=swap"
    ),
    "classic": (
        "https://fonts.googleapis.com/css2?"
        "family=Playfair+Display:wght@400;500;600;700"
        "&family=Source+Sans+3:wght@300;400;500;600;700&display=swap"
    ),
}

_FONT_PREVIEW_FAMILIES = {
    "editorial": "'Libre Bodoni', Georgia, serif",
    "modern": "'Inter', sans-serif",
    "classic": "'Playfair Display', Georgia, serif",
}

_COLOR_PREVIEW_SWATCHES = {
    "light": {"background": "#fafafa", "foreground": "#18181b"},
    "dark": {"background": "#0b0b0d", "foreground": "#fafafa"},
}

whatsapp_number_validator = RegexValidator(
    regex=r"^\+?[\d\s]{8,20}$",
    message=(
        "Numéro invalide. Utilisez un format international, "
        "ex : +33612345678 (8 à 15 chiffres, espaces autorisés)."
    ),
)


class SiteSettings(models.Model):
    class FontTheme(models.TextChoices):
        EDITORIAL = "editorial", "Éditorial (Libre Bodoni / Public Sans)"
        MODERN = "modern", "Moderne (Inter)"
        CLASSIC = "classic", "Classique (Playfair Display / Source Sans 3)"

    class ColorTheme(models.TextChoices):
        LIGHT = "light", "Clair"
        DARK = "dark", "Sombre"

    font_theme = models.CharField(
        max_length=20, choices=FontTheme.choices, default=FontTheme.EDITORIAL,
        help_text="Police utilisée sur l'ensemble du site.",
    )
    color_theme = models.CharField(
        max_length=10, choices=ColorTheme.choices, default=ColorTheme.LIGHT,
        help_text="Thème de couleur utilisé sur l'ensemble du site.",
    )

    whatsapp_number = models.CharField(
        max_length=20, blank=True,
        validators=[whatsapp_number_validator],
        help_text="Format international, ex : +33612345678",
    )
    youtube_url = models.URLField(blank=True, help_text="Lien vers la chaîne YouTube.")
    facebook_url = models.URLField(blank=True, help_text="Lien vers la page Facebook.")
    demo_url = models.URLField(blank=True, help_text="Lien vers la démo des produits.")
    presentation_video_url = models.URLField(
        blank=True,
        help_text="Lien YouTube de la vidéo de présentation (affichée sur l'accueil).",
    )

    class Meta:
        verbose_name = "Réglages du site"
        verbose_name_plural = "Réglages du site"

    def __str__(self):
        return "Réglages du site"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Le singleton ne peut pas être supprimé depuis l'admin."""

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def google_fonts_url(self):
        return _GOOGLE_FONTS_URLS.get(self.font_theme, "")

    @property
    def font_preview_family(self):
        return _FONT_PREVIEW_FAMILIES.get(self.font_theme, "inherit")

    @property
    def color_preview_swatch(self):
        return _COLOR_PREVIEW_SWATCHES.get(self.color_theme, _COLOR_PREVIEW_SWATCHES["light"])

    @property
    def whatsapp_link(self):
        digits = re.sub(r"\D", "", self.whatsapp_number or "")
        return f"https://wa.me/{digits}" if digits else ""

    @property
    def youtube_embed_url(self):
        return youtube_embed_url(self.presentation_video_url)
