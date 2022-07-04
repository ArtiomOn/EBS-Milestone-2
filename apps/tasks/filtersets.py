from django_filters.rest_framework import FilterSet

from apps.tasks.models import Task


class TaskFilterSet(FilterSet):
    class Meta:
        model = Task
        fields = ('title',)