from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Sum

from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
)
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from wkhtmltopdf.views import PDFTemplateResponse

from apps.tasks.filtersets import TaskFilterSet
from apps.tasks.models import (
    Task,
    Comment,
    TimeLog,
    Attachment,
    Project
)
from apps.tasks.serializers import (
    TaskSerializer,
    TaskListSerializer,
    TaskAssignNewUserSerializer,
    TaskUpdateStatusSerializer,
    CommentSerializer,
    TimeLogSerializer,
    TimeLogCreateSerializer,
    TimeLogUserDetailSerializer,
    AttachmentSerializer,
    ProjectSerializer
)
from config import settings

from config.settings import AUTH_USER_MODEL as User

# User = get_user_model()

__all__ = [
    'TaskViewSet',
    'TaskCommentViewSet',
    'TaskTimeLogViewSet',
    'TimeLogViewSet',
    'AttachmentViewSet',
    'ProjectViewSet'
]


class TaskViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    GenericViewSet
):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    filter_backends = [filters.SearchFilter]
    filterset_class = TaskFilterSet
    search_fields = ['title']

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.annotate(duration=Sum('time_logs__duration'))
        return super(TaskViewSet, self).get_queryset()

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return super(TaskViewSet, self).get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(assigned_to=[self.request.user])

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
        self.send_email_task(
            message=f'Task with id:{instance.id} is assigned to you',
            subject='Task assign to you',
            recipient_list=[user_email]
        )
        return Response(status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='update_task_status', serializer_class=TaskUpdateStatusSerializer)
    def update_status(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(status=True)

        user_email = set(Comment.objects.select_related(
            'task__assigned_to').filter(task_id=instance.id).values_list('assigned_to__email', flat=True))
        if user_email:
            self.send_email_task(
                message='commented task is completed',
                subject='commented task is completed',
                recipient_list=list(user_email)
            )

        return Response(status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def task_list_convert_pdf(self, request, *args, **kwargs):
        task_queryset = Task.objects.all()
        comment_queryset = Comment.objects.all()
        timelog_queryset = TimeLog.objects.all()

        template_name = 'tasks/task_list.html',
        context = {
            'tasks': task_queryset,
            'comments': comment_queryset,
            'timelogs': timelog_queryset
        }

        return PDFTemplateResponse(
            request=request,
            context=context,
            template=template_name,
            filename='task_list.pdf'
        )

    @action(methods=['get'], detail=True)
    def task_detail_convert_pdf(self, request, *args, **kwargs):
        template_name = '../templates/tasks/task_detail.html'
        instance = self.get_object()
        task_queryset = self.get_queryset().filter(id=instance.id)
        comments = Comment.objects.filter(task_id=instance.id)
        timelogs = TimeLog.objects.filter(task_id=instance.id)

        context = {
            'tasks': task_queryset,
            'comments': comments,
            'timelogs': timelogs
        }

        return PDFTemplateResponse(
            request=request,
            context=context,
            template=template_name,
            filename='task_detail.pdf')

    @classmethod
    def send_email_task(cls, message, subject, recipient_list):
        send_mail(
            message=message,
            subject=subject,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
            fail_silently=False
        )


class TaskCommentViewSet(
    ListModelMixin,
    CreateModelMixin,
    GenericViewSet
):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.filter(task_id=self.kwargs.get('task__pk'))
        return super(TaskCommentViewSet, self).get_queryset()

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task__pk')
        serializer.save(assigned_to=self.request.user, task_id=task_id)

        user_email = Task.objects.select_related(
            'assigned_to').filter(id=task_id).values_list('assigned_to__email', flat=True)

        self.send_email_comment(
            message=f'You task with id:{task_id} is commented',
            subject='Your task is commented',
            recipient_list=list(user_email)
        )

    @classmethod
    def send_email_comment(cls, message, subject, recipient_list):
        send_mail(
            message=message,
            subject=subject,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
            fail_silently=False
        )


class TaskTimeLogViewSet(
    ListModelMixin,
    CreateModelMixin,
    GenericViewSet
):
    queryset = TimeLog.objects.all()
    serializer_class = TimeLogSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == 'create':
            return TimeLogCreateSerializer
        return super(TaskTimeLogViewSet, self).get_serializer_class()

    def perform_create(self, serializer):
        duration = timedelta(minutes=self.request.data['duration'])
        serializer.save(
            task_id=self.kwargs.get('task__pk'),
            user=self.request.user,
            duration=duration
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(task_id=self.kwargs.get('task__pk'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], url_path='start_timer', detail=False)
    def start_timer(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.create(
            task_id=self.kwargs.get('task__pk'),
            user=self.request.user,
            started_at=datetime.now()
        )
        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['get'], url_path='stop_timer', detail=False)
    def stop_timer(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        instance = queryset.filter(
            duration=None,
            user=self.request.user
        ).first()
        instance.duration = datetime.now() - instance.started_at
        instance.save()
        return Response(status=status.HTTP_200_OK)


class TimeLogViewSet(
    ListModelMixin,
    GenericViewSet
):
    queryset = TimeLog.objects.all()
    serializer_class = TimeLogUserDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.filter_queryset(self.queryset.order_by('-duration'))[:5]

    @action(methods=['get'], detail=False, url_path='time_logs_month')
    def time_log_month(self, request, *args, **kwargs):
        queryset = self.queryset.filter(
            user=self.request.user,
            started_at__month=TimeLog.current_month(),
        )
        serializer = self.get_serializer(queryset, many=True)
        serializer.total_time = queryset.aggregate(Sum('duration'))
        return Response(serializer.total_time)


class AttachmentViewSet(
    ListModelMixin,
    CreateModelMixin,
    GenericViewSet
):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    parser_classes = (MultiPartParser,)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(
            user=self.request.user
        )
        return Response(self.get_serializer(instance=instance).data)


class ProjectViewSet(
    GenericViewSet
):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (AllowAny,)

    @action(methods=['get'], detail=True)
    def project_convert_pdf(self, request, *args, **kwargs):
        instance = self.get_object()
        project = Project.objects.filter(id=instance.id)
        task = Task.objects.filter(project_id=instance.id)
        task_id = list(Task.objects.filter(project_id=instance.id).values_list('id', flat=True))
        comment = Comment.objects.filter(task_id__in=task_id)
        timelog = TimeLog.objects.filter(task_id__in=task_id)

        context = {
            'projects': project,
            'tasks': task,
            'comments': comment,
            'timelogs': timelog
        }

        template_name = '../templates/tasks/project_detail.html'

        return PDFTemplateResponse(
            request=request,
            context=context,
            template=template_name,
            filename='project_detail.pdf')
