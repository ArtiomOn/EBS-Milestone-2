from django_filters.rest_framework import FilterSet

from apps.tasks.models import Task

__all__ = [
    'TaskFilterSet'
]


class TaskFilterSet(FilterSet):
    class Meta:
        model = Task
        fields = ('title',)
