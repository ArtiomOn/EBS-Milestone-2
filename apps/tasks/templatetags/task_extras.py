from django.db.models import QuerySet
from django.template.loader_tags import register


@register.filter
def in_task(queryset, task) -> QuerySet:
    return queryset.filter(task=task)
