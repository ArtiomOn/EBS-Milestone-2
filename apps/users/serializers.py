from django.contrib.auth import get_user_model

from rest_framework import serializers

User = get_user_model()

__all__ = [
    'UserSerializer'
]


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password")
