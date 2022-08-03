from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.core.mail import send_mail

from apps.tasks.models import (
    Task,
    Comment,
    TimeLog,
)
from config import settings


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
    actions = [send_user_email]

    def save_related(self, request, form, formsets, change):
        task_id = form.instance.id
        queryset = super(TaskAdmin, self).get_queryset(request).filter(pk=task_id)
        user_email = queryset.select_related('assigned_to').values_list('assigned_to__email', flat=True)
        change_data = form.changed_data
        status = queryset.values_list('status', flat=True).filter().first()
        if change_data == ['status'] and status is False:
            send_mail(
                message=f'Admin changed you task status to Undone!',
                subject=f'You have one undone Task. Id:{task_id}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=list(user_email),
                fail_silently=False
            )
        return super(TaskAdmin, self).save_related(request, form, formsets, change)


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('id', 'task_id', 'assigned_to')


@admin.register(TimeLog)
class TimeLogAdmin(ModelAdmin):
    list_display = ('id', 'task', 'user', 'started_at', 'duration')
