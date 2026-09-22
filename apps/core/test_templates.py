from django.test import TestCase
from django.urls import reverse

from .models import SiteSettings


class BaseTemplateThemeAttributesTests(TestCase):
    def test_html_tag_reflects_configured_color_and_font_theme(self):
        settings_obj = SiteSettings.get_solo()
        settings_obj.color_theme = SiteSettings.ColorTheme.DARK
        settings_obj.font_theme = SiteSettings.FontTheme.MODERN
        settings_obj.save()

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, 'data-theme="dark"')
        self.assertContains(response, 'data-font="modern"')

    def test_google_fonts_link_matches_font_theme(self):
        settings_obj = SiteSettings.get_solo()
        settings_obj.font_theme = SiteSettings.FontTheme.CLASSIC
        settings_obj.save()

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "Playfair")


class ContactLinksTests(TestCase):
    def test_no_contact_links_rendered_when_unconfigured(self):
        response = self.client.get(reverse("core:home"))

        self.assertNotContains(response, "wa.me")
        self.assertNotContains(response, "aria-label=\"WhatsApp\"")
        self.assertNotContains(response, "aria-label=\"YouTube\"")
        self.assertNotContains(response, "aria-label=\"Facebook\"")

    def test_configured_contact_links_are_rendered(self):
        settings_obj = SiteSettings.get_solo()
        settings_obj.whatsapp_number = "+33612345678"
        settings_obj.youtube_url = "https://youtube.com/@example"
        settings_obj.facebook_url = "https://facebook.com/example"
        settings_obj.demo_url = "https://demo.example.com"
        settings_obj.save()

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "https://wa.me/33612345678")
        self.assertContains(response, "https://youtube.com/@example")
        self.assertContains(response, "https://facebook.com/example")
        self.assertContains(response, "https://demo.example.com")


class PresentationVideoTests(TestCase):
    def test_no_video_section_when_unconfigured(self):
        response = self.client.get(reverse("core:home"))
        self.assertNotContains(response, "youtube.com/embed")

    def test_video_iframe_rendered_when_configured(self):
        settings_obj = SiteSettings.get_solo()
        settings_obj.presentation_video_url = "https://youtu.be/dQw4w9WgXcQ"
        settings_obj.save()

        response = self.client.get(reverse("core:home"))

        self.assertContains(
            response, "https://www.youtube.com/embed/dQw4w9WgXcQ"
        )
