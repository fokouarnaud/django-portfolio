from django.test import TestCase
from django.urls import reverse

from apps.projects.tests import make_project
from apps.projects.models import Project


class HomeViewTests(TestCase):
    def test_home_shows_only_published_projects(self):
        published = make_project(slug="published-project")
        draft = make_project(
            slug="draft-project",
            title="Draft",
            status=Project.Status.DRAFT,
            published_at=None,
        )

        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertIn(published, response.context["projects"])
        self.assertNotIn(draft, response.context["projects"])

    def test_home_limits_to_three_recent_projects(self):
        for i in range(5):
            make_project(slug=f"project-{i}", title=f"Project {i}")

        response = self.client.get(reverse("core:home"))

        self.assertEqual(len(response.context["projects"]), 3)


class AboutViewTests(TestCase):
    def test_about_page_returns_200(self):
        response = self.client.get(reverse("core:about"))
        self.assertEqual(response.status_code, 200)
