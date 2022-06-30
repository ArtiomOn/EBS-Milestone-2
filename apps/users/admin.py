from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'is_staff')
