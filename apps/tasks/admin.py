from django.contrib import admin
from django.contrib.admin import ModelAdmin, SimpleListFilter
from django.core.mail import send_mail

from rest_framework.exceptions import NotFound

from apps.tasks.models import (
    Task,
    Comment,
    TimeLog,
    File
)
from config import settings


class FileSizeFilter(SimpleListFilter):
    title = 'File size filter'

    parameter_name = 'file_size'

    def lookups(self, request, model_admin):
        return (
            ('1Mb', ('≤1Mb')),
            ('5Mb', ('≤5Mb')),
            ('10Mb', ('≤10Mb')),
            ('20Mb', ('≤20Mb')),
            ('50Mb', ('≤50Mb')),
            ('100Mb', ('≤100Mb')),
        )

    def queryset(self, request, queryset):
        if self.value() == '1Mb':
            return queryset.filter(
                file_size__lte=1000
            )
        if self.value() == '5Mb':
            return queryset.filter(
                file_size__lte=5000
            )
        if self.value() == '10Mb':
            return queryset.filter(
                file_size__lte=10000
            )
        if self.value() == '20Mb':
            return queryset.filter(
                file_size__lte=20000
            )
        if self.value() == '50Mb':
            return queryset.filter(
                file_size__lte=50000
            )
        if self.value() == '100Mb':
            return queryset.filter(
                file_size__lte=100000
            )


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
    search_fields = ('title',)
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


@admin.register(TimeLog)
class TimeLogAdmin(ModelAdmin):
    list_display = ('id', 'task', 'user', 'started_at', 'duration')


@admin.register(File)
class FileAdmin(ModelAdmin):
    list_display = ('id', 'title', 'file_url', 'extension', 'file_size', 'user_id', 'task_id', 'comment_id')
    list_filter = (FileSizeFilter, 'extension', 'user', 'task', 'comment')
    search_fields = ('title', 'file_url')

    def save_model(self, request, obj, form, change):
        update_fields = []
        for key, value in form.cleaned_data.items():
            if value != form.initial[key]:
                update_fields.append(key)

        obj.save(update_fields=update_fields)
