from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.core.signals import request_finished

from rest_framework.exceptions import NotFound

from apps.tasks.models import (
    Task,
    Comment,
    TimeLog,
)
from config import settings


@admin.action(description='Update task status to True')
def update_task_status_true(model_admin, request, queryset):
    status = queryset.values_list('status', flat=True)
    if not all(list(status)):
        queryset.update(status=True)
    else:
        raise NotFound


@admin.action(description='Update task status to False')
def update_task_status_false(model_admin, request, queryset):
    task_id = list(queryset.values_list('id', flat=True))
    status = queryset.values_list('status', flat=True)
    if all(list(status)):
        for (task_status, tasks_id) in zip(status, task_id):
            queryset.filter(pk__in=[tasks_id]).update(status=False)
            user_email = queryset.filter(pk__in=[tasks_id]).select_related('assigned_to').values_list(
                'assigned_to__email', flat=True)
            send_mail(
                message='Admin changed you task status to Undone!',
                subject=f'You have one undone Task. ID: {tasks_id}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=list(user_email),
                fail_silently=False
            )
    else:
        raise NotFound


@admin.action(description='Send email to user')
def send_user_email(model_admin, request, queryset):
    queryset = queryset.select_related('assigned_to').values_list('assigned_to__email', flat=True)
    send_mail(
        message='test message from django admin',
        subject='test subject from django admin',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=list(queryset),
        fail_silently=False
    )


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = ('id', 'title', 'status', 'assigned_to')
    list_filter = ('status',)
    search_fields = ('title', )
    actions = [
        update_task_status_false,
        update_task_status_true,
        send_user_email
    ]

    def save_model(self, request, obj, form, change):
        update_fields = []
        for key, value in form.cleaned_data.items():
            if value != form.initial[key]:
                update_fields.append(key)

        obj.save(update_fields=update_fields)


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('id', 'task_id', 'assigned_to')

    def save_model(self, request, obj, form, change):
        update_fields = []
        for key, value in form.cleaned_data.items():
            if value != form.initial[key]:
                update_fields.append(key)

        obj.save(update_fields=update_fields)


@admin.register(TimeLog)
class TimeLogAdmin(ModelAdmin):
    list_display = ('id', 'task', 'user', 'started_at', 'duration')

    def save_model(self, request, obj, form, change):
        update_fields = []
        for key, value in form.cleaned_data.items():
            if value != form.initial[key]:
                update_fields.append(key)

        obj.save(update_fields=update_fields)
