import markdown as md
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdownify")
@stringfilter
def markdownify(value):
    return mark_safe(md.markdown(value, extensions=["fenced_code", "tables"]))
