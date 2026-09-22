import base64

from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .admin import ProjectAdmin, TagListFilter
from .filters import ProjectFilter
from .models import Project

# 1x1 transparent PNG, valid enough for Pillow to accept as an ImageField.
_PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY"
    "42YAAAAASUVORK5CYII="
)


def make_project(**overrides):
    defaults = dict(
        title="Sample project",
        slug="sample-project",
        short_description="A short description",
        long_description="**Long** description",
        cover_image=SimpleUploadedFile("cover.png", _PNG_1X1, content_type="image/png"),
        status=Project.Status.PUBLISHED,
        published_at=timezone.now(),
    )
    defaults.update(overrides)
    return Project.objects.create(**defaults)


class ProjectModelTests(TestCase):
    def test_str_returns_title(self):
        project = make_project(title="My Portfolio Item", slug="my-portfolio-item")
        self.assertEqual(str(project), "My Portfolio Item")

    def test_get_absolute_url(self):
        project = make_project(slug="my-slug")
        self.assertEqual(
            project.get_absolute_url(),
            reverse("projects:project_detail", kwargs={"slug": "my-slug"}),
        )

    def test_published_manager_excludes_drafts(self):
        make_project(slug="draft-project", status=Project.Status.DRAFT, published_at=None)
        published = make_project(slug="published-project")

        self.assertEqual(list(Project.published.all()), [published])

    def test_published_manager_excludes_future_publish_date(self):
        future = timezone.now() + timezone.timedelta(days=1)
        make_project(slug="future-project", published_at=future)

        self.assertEqual(list(Project.published.all()), [])

    def test_saving_as_published_without_date_sets_published_at_to_now(self):
        project = make_project(
            slug="auto-date-project", status=Project.Status.PUBLISHED, published_at=None
        )

        self.assertIsNotNone(project.published_at)
        self.assertLessEqual(project.published_at, timezone.now())

    def test_saving_as_draft_does_not_set_published_at(self):
        project = make_project(
            slug="draft-project", status=Project.Status.DRAFT, published_at=None
        )

        self.assertIsNone(project.published_at)

    def test_saving_as_published_keeps_explicit_published_at(self):
        explicit_date = timezone.now() - timezone.timedelta(days=10)
        project = make_project(slug="explicit-date-project", published_at=explicit_date)

        self.assertEqual(project.published_at, explicit_date)


class ProjectFilterTests(TestCase):
    def setUp(self):
        self.django_project = make_project(
            title="Django project", slug="django-project"
        )
        self.django_project.tags.add("django", "python")

        self.vue_project = make_project(title="Vue project", slug="vue-project")
        self.vue_project.tags.add("vue", "javascript")

    def test_filter_by_tag(self):
        result = ProjectFilter(
            {"tag": "django"}, queryset=Project.published.all()
        ).qs
        self.assertEqual(list(result), [self.django_project])

    def test_filter_by_year(self):
        year = timezone.now().year
        result = ProjectFilter(
            {"year": str(year)}, queryset=Project.published.all()
        ).qs
        self.assertEqual(result.count(), 2)

    def test_filter_by_search_query_matches_tag_name(self):
        result = ProjectFilter(
            {"q": "javascript"}, queryset=Project.published.all()
        ).qs
        self.assertEqual(list(result), [self.vue_project])


class TagListFilterTests(TestCase):
    def test_queryset_filters_by_selected_tag_slug(self):
        tagged = make_project(slug="tagged-project")
        tagged.tags.add("featured")
        make_project(slug="other-project", title="Other")

        admin_instance = ProjectAdmin(Project, AdminSite())
        list_filter = TagListFilter(
            request=None,
            params={"tag": ["featured"]},
            model=Project,
            model_admin=admin_instance,
        )

        result = list_filter.queryset(None, Project.objects.all())
        self.assertEqual(list(result), [tagged])


class ProjectAdminFormTests(TestCase):
    def setUp(self):
        self.admin_instance = ProjectAdmin(Project, AdminSite())

    def test_cover_thumbnail_renders_image_tag_when_image_present(self):
        project = make_project(slug="with-cover")

        html = self.admin_instance.cover_thumbnail(project)

        self.assertIn("<img", html)
        self.assertIn(project.cover_image.url, html)

    def test_cover_thumbnail_shows_placeholder_without_pk(self):
        unsaved_project = Project(title="Not saved yet")

        html = self.admin_instance.cover_thumbnail(unsaved_project)

        self.assertNotIn("<img", html)

    def test_short_description_widget_has_maxlength_attribute(self):
        form = self.admin_instance.get_form(request=None)()

        widget_attrs = form.fields["short_description"].widget.attrs

        self.assertEqual(widget_attrs.get("maxlength"), "300")


class ProjectViewTests(TestCase):
    def setUp(self):
        self.published = make_project(slug="published-project")
        self.draft = make_project(
            slug="draft-project",
            title="Draft project",
            status=Project.Status.DRAFT,
            published_at=None,
        )

    def test_list_view_shows_only_published_projects(self):
        response = self.client.get(reverse("projects:project_list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.published, response.context["projects"])
        self.assertNotIn(self.draft, response.context["projects"])

    def test_detail_view_404_for_draft_as_anonymous(self):
        response = self.client.get(
            reverse("projects:project_detail", kwargs={"slug": self.draft.slug})
        )
        self.assertEqual(response.status_code, 404)

    def test_detail_view_200_for_published_project(self):
        response = self.client.get(
            reverse("projects:project_detail", kwargs={"slug": self.published.slug})
        )
        self.assertEqual(response.status_code, 200)
