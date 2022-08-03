from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from config import settings

User = get_user_model()

__all__ = [
    'Task',
    'Comment',
    'TimeLog'
]


class Task(models.Model):
    title = models.CharField(
        max_length=50
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


@receiver(post_save, sender=Task, dispatch_uid='send_email_user')
def send_email_user(sender, instance, **kwargs):
    change_data = kwargs['update_fields']
    status = instance.status
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
