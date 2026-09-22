from django.views.generic import ListView, TemplateView

from apps.projects.models import Project


class HomeView(ListView):
    model = Project
    template_name = "core/home.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.published.all()[:3]


class AboutView(TemplateView):
    template_name = "core/about.html"
