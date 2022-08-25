from pathlib import Path
from typing import Union

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db import models
from django.db.models import QuerySet, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from guardian.shortcuts import assign_perm
from rest_framework.request import Request
from wkhtmltopdf.views import PDFTemplateResponse

User = settings.AUTH_USER_MODEL

__all__ = [
    'Task',
    'Comment',
    'TimeLog',
    'Attachment',
    'Project',
    'TaskQuerySet',
    'ProjectQuerySet'
]


# noinspection PyTypeChecker
class TaskQuerySet(QuerySet):
    def allowed_to(self, user: User) -> 'TaskQuerySet':
        return self.filter(
            project_id__in=Project.objects.allowed_to(user).values('id')
        )

    def with_duration(self) -> 'TaskQuerySet':
        return self.annotate(
            duration=Sum('time_logs__duration')
        )

    @staticmethod
    def assign_user_permission(user: User):
        assign_perm('tasks.view_task', user)
        assign_perm('tasks.add_task', user)
        assign_perm('tasks.delete_task', user)
        assign_perm('tasks.change_task', user)


class Task(models.Model):
    objects = TaskQuerySet.as_manager()

    title = models.CharField(
        max_length=50,
    )
    description = models.TextField()
    status = models.BooleanField(
        default=False,
        verbose_name='Completed'
    )
    assigned_to = models.ManyToManyField(
        User,
        related_name='tasks'
    )
    attachment = models.ManyToManyField(
        'Attachment',
        related_name='task_attachments',
        blank=True
    )
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        null=False,
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.title

    @staticmethod
    def send_user_email(message: str, subject: str, recipient: Union[QuerySet, set]):
        send_mail(
            message=message,
            subject=subject,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient],
            fail_silently=False
        )

    @staticmethod
    def html_convert_pdf(request: Request, template: str, context: dict, filename: str):
        # Convert html file to pdf
        return PDFTemplateResponse(
            request=request,
            context=context,
            template=template,
            filename=filename
        )


class Comment(models.Model):
    text = models.TextField()
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        related_name='comments'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    attachment = models.ManyToManyField(
        'Attachment',
        related_name='comment_attachments',
        blank=True
    )

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return f'{self.id}'


class TimeLog(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        related_name='time_logs'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='time_logs'
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True
    )
    is_started = models.BooleanField(
        default=False
    )
    is_stopped = models.BooleanField(
        default=False
    )
    duration = models.DurationField(
        null=True,
        blank=True
    )
    attachment = models.ManyToManyField(
        'Attachment',
        related_name='timelog_attachments',
        blank=True
    )

    class Meta:
        verbose_name = 'Time Log'
        verbose_name_plural = 'Time Logs'

    def __str__(self):
        return f'{self.id}'


class Attachment(models.Model):
    title = models.CharField(
        max_length=75,
    )
    file_url = models.FileField(
        blank=True
    )
    extension = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )
    file_size = models.IntegerField(
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='attachments'
    )

    class Meta:
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.file_size = self.file_url.size
        self.extension = Path(self.file_url.name).suffix
        super(Attachment, self).save(force_insert, force_update, using, update_fields)


# noinspection PyTypeChecker
class ProjectQuerySet(QuerySet):
    def allowed_to(self, user: User) -> 'ProjectQuerySet':
        return self.filter(
            id__in=Project.objects.filter(member__id=user.id)
        )


class Project(models.Model):
    objects = ProjectQuerySet.as_manager()

    name = models.CharField(
        max_length=150
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    member = models.ManyToManyField(
        User,
        blank=True,
        related_name='projects'
    )
    logo = models.ManyToManyField(
        'Attachment',
        blank=True
    )
    description = models.TextField(
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return self.name


@receiver(post_save, sender=Task, dispatch_uid='send_email_user')
def send_email_user(sender, instance, **kwargs):
    change_data = kwargs['update_fields']
    status = instance.status
    if change_data is not None:
        if 'status' in change_data and status is False:
            user_email = Task.objects.filter(
                pk=instance.id
            ).select_related(
                'assigned_to'
            ).values_list(
                'assigned_to__email',
                flat=True
            )
            send_mail(
                message=f'Admin changed you task status to Undone!',
                subject=f'You have one undone Task. Id:{instance.id}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=list(user_email),
                fail_silently=False
            )
