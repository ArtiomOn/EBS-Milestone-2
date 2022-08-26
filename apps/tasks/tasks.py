from celery import shared_task
from django.core.mail import send_mail

from apps.tasks.models import Task
from django.conf import settings

__all__ = [
    'send_email'
]


@shared_task
def send_email() -> None:
    # Send email to all people that have status False on their task
    user_email: set = set(Task.objects.select_related(
        'assigned_to'
    ).filter(
        status=False
    ).values_list(
        'assigned_to__email',
        flat=True
    ))
    send_mail(
        message='Your task is not completed',
        subject='Your task in not completed',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=list(user_email),
        fail_silently=False
    )
