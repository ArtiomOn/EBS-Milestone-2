from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.core.mail import send_mail
from django.db.models.signals import post_save

from apps.tasks.models import (
    Task,
    Comment,
    TimeLog,
)
from config import settings


@admin.action(description='Update task status')
def update_task_status(model_admin, request, queryset):
    task_id = list(queryset.values_list('id', flat=True))
    status = queryset.values_list('status', flat=True)
    for (task_status, tasks_id) in zip(status, task_id):
        if task_status is True:
            queryset.filter(pk__in=[tasks_id]).update(status=False)
        else:
            queryset.filter(pk__in=[tasks_id]).update(status=True)

    post_save.send(sender=Task, instance=queryset, action_change_status=True, task_id=task_id)


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
    actions = [update_task_status, send_user_email]

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
