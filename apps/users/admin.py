from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db.models import QuerySet

from apps.users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'is_staff')

    # noinspection DuplicatedCode
    def save_model(self, request, obj, form, change):
        ignored_keys = []
        update_fields = []
        if bool(form.initial):
            for key, value in form.cleaned_data.items():
                if isinstance(value, QuerySet):
                    ignored_keys.append(key)
                if value != form.initial[key]:
                    update_fields.append(key)
            return obj.save(
                update_fields=set(update_fields) - set(ignored_keys)
            )
        return super(CustomUserAdmin, self).save_model(request, obj, form, change)
