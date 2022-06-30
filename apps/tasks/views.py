from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
)

from apps.tasks.models import Task
from apps.tasks.serializers import (
    TaskSerializer,
    TaskListSerializer,
    TaskAssignNewUserSerializer,
    TaskUpdateStatusSerializer,
)

User = get_user_model()


class TaskViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (AllowAny,)
    authentication_classes = [JWTAuthentication]

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return super(TaskViewSet, self).get_serializer_class()

    def perform_create(self, serializer):
        serializer.save()  # Todo change to the line below | remove bug with AnonymousUser
        # serializer.save(assigned_to=self.request.user) TODO correct variant

    @action(methods=['get'], url_path='my_task', detail=False, serializer_class=TaskListSerializer)
    def my_task(self, request, *args, **kwargs):
        queryset = self.queryset.filter(assigned_to=User.objects.get(id=1))  # TODO change to the line below
        # queryset = self.queryset.filter(assigned_to=request.user) TODO correct variant
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], url_path='completed_task', detail=False, serializer_class=TaskListSerializer)
    def complete_task(self, request, *args, **kwargs):
        queryset = self.queryset.filter(status=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['patch'], detail=True, url_path='assign_user', serializer_class=TaskAssignNewUserSerializer)
    def assign(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance.assigned_to = serializer.validated_data['assigned_to']
        return Response(status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='update_task_status', serializer_class=TaskUpdateStatusSerializer)
    def update_status(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance.status = True
        instance.save()
        return Response(status=status.HTTP_200_OK)
