from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.tasks.models import Task


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = ('id', 'title', 'status', 'assigned_to')
