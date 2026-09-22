from django.test import TestCase
from django.urls import reverse

from .models import SiteSettings


class SiteSettingsContextProcessorTests(TestCase):
    def test_site_settings_is_available_in_template_context(self):
        response = self.client.get(reverse("core:home"))

        self.assertIn("site_settings", response.context)
        self.assertEqual(response.context["site_settings"].pk, SiteSettings.get_solo().pk)

    def test_site_settings_reflects_saved_values(self):
        settings_obj = SiteSettings.get_solo()
        settings_obj.facebook_url = "https://facebook.com/example"
        settings_obj.save()

        response = self.client.get(reverse("core:about"))

        self.assertEqual(
            response.context["site_settings"].facebook_url,
            "https://facebook.com/example",
        )
