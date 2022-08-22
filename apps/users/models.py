from pathlib import Path

from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from apps.tasks.models import Attachment

__all__ = [
    'CustomUserManager',
    'CustomUser'
]


class CustomUserManager(UserManager):

    def create_superuser(self, email=None, password=None, **extra_fields):
        return super(CustomUserManager, self).create_superuser(email, password, **extra_fields)


class CustomUser(AbstractUser):
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
    objects = CustomUserManager()

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    class Meta:
        app_label = 'users'


@receiver(pre_save, sender=CustomUser, dispatch_uid='check_image_extension')
def send_email_user(sender, instance, **kwargs):
    instance: CustomUser = instance
    if instance.profile_image is not None:
        extension = Path(instance.profile_image.file_url.name).suffix
        if extension not in ['.jpg', '.png', '.jpeg']:
            raise ValueError('Extensions are jpg, png, jpeg')
