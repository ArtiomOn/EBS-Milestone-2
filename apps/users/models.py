from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager, AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models import EmailField


class CustomUserManager(UserManager):

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        return super(CustomUserManager, self).create_superuser(username, email, password, **extra_fields)

    def _create_user(self, username=None, email=None, password=None, **extra_fields):
        email = self.normalize_email(email)

        user = self.model(email=email, username=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):

    objects = CustomUserManager()
    email = EmailField(_('email address'), blank=False, unique=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'
