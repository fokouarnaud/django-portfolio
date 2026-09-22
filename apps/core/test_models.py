from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import SiteSettings


class SiteSettingsSingletonTests(TestCase):
    def test_get_solo_creates_the_row_on_first_call(self):
        self.assertEqual(SiteSettings.objects.count(), 0)
        settings_obj = SiteSettings.get_solo()
        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(settings_obj.pk, 1)

    def test_get_solo_returns_the_same_row_on_later_calls(self):
        first = SiteSettings.get_solo()
        first.whatsapp_number = "+33612345678"
        first.save()

        second = SiteSettings.get_solo()

        self.assertEqual(second.pk, first.pk)
        self.assertEqual(second.whatsapp_number, "+33612345678")

    def test_save_always_forces_primary_key_to_one(self):
        settings_obj = SiteSettings(pk=42)
        settings_obj.save()

        self.assertEqual(settings_obj.pk, 1)
        self.assertEqual(SiteSettings.objects.count(), 1)

    def test_delete_is_a_no_op(self):
        settings_obj = SiteSettings.get_solo()
        settings_obj.delete()

        self.assertEqual(SiteSettings.objects.count(), 1)


class SiteSettingsWhatsappLinkTests(TestCase):
    def test_builds_wa_me_link_from_formatted_number(self):
        settings_obj = SiteSettings(whatsapp_number="+33 6 12 34 56 78")
        self.assertEqual(settings_obj.whatsapp_link, "https://wa.me/33612345678")

    def test_empty_link_when_no_number_configured(self):
        settings_obj = SiteSettings(whatsapp_number="")
        self.assertEqual(settings_obj.whatsapp_link, "")

    def test_rejects_non_numeric_whatsapp_number(self):
        settings_obj = SiteSettings(whatsapp_number="not-a-number")
        with self.assertRaises(ValidationError):
            settings_obj.full_clean()

    def test_rejects_too_short_whatsapp_number(self):
        settings_obj = SiteSettings(whatsapp_number="+123")
        with self.assertRaises(ValidationError):
            settings_obj.full_clean()

    def test_accepts_valid_international_whatsapp_number(self):
        settings_obj = SiteSettings(whatsapp_number="+33 6 12 34 56 78")
        settings_obj.full_clean()

    def test_blank_whatsapp_number_is_valid(self):
        settings_obj = SiteSettings(whatsapp_number="")
        settings_obj.full_clean()


class SiteSettingsYoutubeEmbedTests(TestCase):
    def test_embed_url_derived_from_presentation_video_url(self):
        settings_obj = SiteSettings(
            presentation_video_url="https://youtu.be/dQw4w9WgXcQ"
        )
        self.assertEqual(
            settings_obj.youtube_embed_url,
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
        )

    def test_empty_embed_url_when_no_video_configured(self):
        settings_obj = SiteSettings(presentation_video_url="")
        self.assertEqual(settings_obj.youtube_embed_url, "")


class SiteSettingsFontThemeTests(TestCase):
    def test_default_font_theme_is_editorial(self):
        settings_obj = SiteSettings.get_solo()
        self.assertEqual(settings_obj.font_theme, SiteSettings.FontTheme.EDITORIAL)

    def test_default_color_theme_is_light(self):
        settings_obj = SiteSettings.get_solo()
        self.assertEqual(settings_obj.color_theme, SiteSettings.ColorTheme.LIGHT)

    def test_google_fonts_url_changes_with_font_theme(self):
        editorial = SiteSettings(font_theme=SiteSettings.FontTheme.MODERN)
        classic = SiteSettings(font_theme=SiteSettings.FontTheme.CLASSIC)

        self.assertIn("Inter", editorial.google_fonts_url)
        self.assertIn("Playfair", classic.google_fonts_url)
        self.assertNotEqual(editorial.google_fonts_url, classic.google_fonts_url)

    def test_font_preview_family_matches_font_theme(self):
        modern = SiteSettings(font_theme=SiteSettings.FontTheme.MODERN)
        classic = SiteSettings(font_theme=SiteSettings.FontTheme.CLASSIC)

        self.assertIn("Inter", modern.font_preview_family)
        self.assertIn("Playfair Display", classic.font_preview_family)
