from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(status=Project.Status.PUBLISHED, published_at__lte=timezone.now())
        )


class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Brouillon"
        PUBLISHED = "published", "Publié"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    short_description = models.CharField(max_length=300)
    long_description = models.TextField(
        help_text="Contenu au format Markdown."
    )
    cover_image = models.ImageField(upload_to="projects/covers/%Y/%m/")
    tags = TaggableManager(blank=True)
    external_link = models.URLField(blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("projects:project_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
