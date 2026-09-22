from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import SiteSettings


class SiteSettingsAdminTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_superuser(
            username="staff", email="staff@example.com", password="pass1234"
        )
        self.client.force_login(self.staff)

    def test_add_permission_denied_once_singleton_exists(self):
        SiteSettings.get_solo()
        add_url = reverse("admin:core_sitesettings_add")

        response = self.client.get(add_url)

        self.assertEqual(response.status_code, 403)

    def test_changelist_redirects_straight_to_the_singleton_change_form(self):
        settings_obj = SiteSettings.get_solo()
        changelist_url = reverse("admin:core_sitesettings_changelist")

        response = self.client.get(changelist_url)

        self.assertRedirects(
            response,
            reverse("admin:core_sitesettings_change", args=[settings_obj.pk]),
        )

    def test_change_form_shows_color_preview_matching_theme(self):
        settings_obj = SiteSettings.get_solo()
        settings_obj.color_theme = SiteSettings.ColorTheme.DARK
        settings_obj.save()
        change_url = reverse("admin:core_sitesettings_change", args=[settings_obj.pk])

        response = self.client.get(change_url)

        self.assertContains(response, "#0b0b0d")

    def test_change_form_shows_font_preview_matching_theme(self):
        settings_obj = SiteSettings.get_solo()
        settings_obj.font_theme = SiteSettings.FontTheme.CLASSIC
        settings_obj.save()
        change_url = reverse("admin:core_sitesettings_change", args=[settings_obj.pk])

        response = self.client.get(change_url)

        self.assertRegex(
            response.content.decode(), r'font-family:[^"]*Playfair Display'
        )

    def test_delete_permission_is_always_denied(self):
        settings_obj = SiteSettings.get_solo()
        delete_url = reverse(
            "admin:core_sitesettings_delete", args=[settings_obj.pk]
        )

        response = self.client.get(delete_url)

        self.assertEqual(response.status_code, 403)
