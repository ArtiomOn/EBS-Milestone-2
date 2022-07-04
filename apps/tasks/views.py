from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from rest_framework import status, filters
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

from apps.tasks.filtersets import TaskFilterSet
from apps.tasks.models import Task, Comment
from apps.tasks.serializers import (
    TaskSerializer,
    TaskListSerializer,
    TaskAssignNewUserSerializer,
    TaskUpdateStatusSerializer,
    CommentSerializer
)
from config import settings

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
    filter_backends = [filters.SearchFilter]
    filterset_class = TaskFilterSet
    search_fields = ['title']

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return super(TaskViewSet, self).get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(assigned_to=self.request.user)

    @action(methods=['get'], url_path='my_task', detail=False, serializer_class=TaskListSerializer)
    def my_task(self, request, *args, **kwargs):
        queryset = self.queryset.filter(assigned_to=request.user)
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
        user_email = User.objects.get(id=instance.assigned_to.id).email
        self.send_email_task(message=f'Task with id:{instance.id} is assigned to you',
                             subject='Task assign to you', recipient_list=[user_email])
        return Response(status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=True, url_path='update_task_status', serializer_class=TaskUpdateStatusSerializer)
    def update_status(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance.status = True
        instance.save()

        comments = Comment.objects.all().filter(task_id=instance.id).values_list('assigned_to', flat=True)
        users_email = User.objects.filter(id__in=comments.all()).values_list('email', flat=True)
        self.send_email_task(message='commented task is completed', subject='commented task is completed',
                             recipient_list=list(users_email))

        return Response(status=status.HTTP_200_OK)

    @classmethod
    def send_email_task(cls, message, subject, recipient_list):
        send_mail(message=message, subject=subject, from_email=settings.EMAIL_HOST_USER,
                  recipient_list=recipient_list, fail_silently=False)


class TaskCommentViewSet(
    ListModelMixin,
    CreateModelMixin,
    GenericViewSet
):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (AllowAny,)
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.filter(task_id=self.kwargs.get('task__pk'))
        return super(TaskCommentViewSet, self).get_queryset()

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task__pk')
        serializer.save(assigned_to=self.request.user, task_id=task_id)

        user_task = Task.objects.get(id=task_id).assigned_to_id
        user_email = User.objects.get(id=user_task).email
        self.send_email_comment(message=f'You task with id:{task_id} is commented',
                                subject='Your task is commented', recipient_list=user_email)

    @classmethod
    def send_email_comment(cls, message, subject, recipient_list):
        send_mail(message=message, subject=subject, from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[recipient_list], fail_silently=False)
