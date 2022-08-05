import os
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from config import settings
from apps.tasks.validators import size

User = get_user_model()

__all__ = [
    'Task',
    'Comment',
    'TimeLog',
    'File'
]


class Task(models.Model):
    title = models.CharField(
        max_length=50,
    )
    description = models.TextField()
    status = models.BooleanField(
        default=False,
        verbose_name='Completed'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True
    )

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField()
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        related_name='comments'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='comments'
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
    duration = models.DurationField(
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Time Log'
        verbose_name_plural = 'Time Logs'

    def __str__(self):
        return f'{self.id}'

    @staticmethod
    def current_month():
        return datetime.now().strftime('%m')


class File(models.Model):
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
        validators=[size],
        blank=True,
        null=True,
        verbose_name=''
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        null=True,
        related_name='files',
        blank=True
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        related_name='files',
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='files'
    )

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'

    def __str__(self):
        return self.title


@receiver(post_save, sender=Task, dispatch_uid='send_email_user')
def send_email_user(sender, instance, **kwargs):
    change_data = kwargs['update_fields']
    status = instance.status
    if change_data is not None:
        if 'status' in change_data and status is False:
            user_email = Task.objects.filter(
                pk=instance.id).select_related('assigned_to').values_list('assigned_to__email', flat=True)
            send_mail(
                message=f'Admin changed you task status to Undone!',
                subject=f'You have one undone Task. Id:{instance.id}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=list(user_email),
                fail_silently=False
            )


@receiver(post_save, sender=File, dispatch_uid='file_path')
def file_path(sender, instance, **kwargs):
    queryset = File.objects.filter(pk=instance.id)
    file_url = instance.file_url.path
    file_size = round(os.path.getsize(file_url)/1024)

    queryset.update(file_size=file_size)
    queryset.update(file_url=file_url)
