from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer

User = get_user_model()


class TaskViewSet(CreateModelMixin, GenericViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (AllowAny,)
    authentication_classes = [JWTAuthentication]

    def perform_create(self, serializer):
        serializer.save()
        # serializer.save(assigned_to=self.request.user) | self.request.user return AnonymousUser
