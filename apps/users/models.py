from pathlib import Path

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager, AbstractUser
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.db.models import EmailField, ManyToManyField

from apps.tasks.models import Attachment


__all__ = [
    'CustomUserManager',
    'CustomUser'
]


class CustomUserManager(UserManager):

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        return super(CustomUserManager, self).create_superuser(username, email, password, **extra_fields)

    def _create_user(self, username=None, email=None, password=None, **extra_fields):
        email = self.normalize_email(email)

        user = self.model(
            email=email,
            username=email,
            **extra_fields
        )
        user.password = make_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    email = EmailField(
        _('email address'),
        blank=False,
        unique=True
    )
    profile_image = ManyToManyField(
        Attachment,
        'user_attachment',
        blank=True
    )
    objects = CustomUserManager()

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    class Meta:
        app_label = 'users'


@receiver(
    signal=m2m_changed,
    sender=CustomUser.profile_image.through,
    dispatch_uid='check_image_extension',
    weak=False
)
def check_image_extension(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'pre_add':
        instance: Attachment = instance
        extension = Path(instance.file_url.name).suffix
        if extension not in ['.jpg', '.png', '.jpeg']:
            raise ValueError('Extensions are jpg, png, jpeg')
