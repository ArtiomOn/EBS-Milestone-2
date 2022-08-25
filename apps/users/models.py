from pathlib import Path

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from apps.tasks.models import Attachment

__all__ = [
    'CustomUser'
]


class CustomUser(AbstractUser):
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    email = models.EmailField(
        _('email address'),
        blank=False,
        unique=True
    )
    profile_image = models.ForeignKey(
        Attachment,
        on_delete=models.SET_NULL,
        related_name='user_attachment',
        blank=True,
        null=True
    )

    class Meta:
        app_label = 'users'


# noinspection PyUnusedLocal
@receiver(pre_save, sender=CustomUser, dispatch_uid='check_image_extension')
def send_email_user(sender, instance, **kwargs):
    if kwargs.get('created', True) and not kwargs.get('raw', False):
        instance: CustomUser = instance
        allowed_extensions = ['.jpg', '.png', '.jpeg']
        if instance.profile_image is not None:
            extension = Path(instance.profile_image.file_url.name).suffix
            if extension not in allowed_extensions:
                raise ValueError(f'Extensions are {[extension for extension in allowed_extensions]}')
