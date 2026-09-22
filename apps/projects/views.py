from django.views.generic import DetailView
from django_filters.views import FilterView
from taggit.models import Tag

from .filters import ProjectFilter
from .models import Project


class ProjectListView(FilterView):
    model = Project
    filterset_class = ProjectFilter
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 9

    def get_queryset(self):
        return Project.published.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_tags"] = Tag.objects.order_by("name")
        context["available_years"] = Project.published.dates(
            "published_at", "year", order="DESC"
        )
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        if self.request.user.is_staff:
            return Project.objects.all()
        return Project.published.all()
