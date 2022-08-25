import datetime
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Sum
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
)
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.tasks.filtersets import TaskFilterSet
from apps.tasks.models import (
    Task,
    Comment,
    TimeLog,
    Attachment,
    Project,
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
    ProjectSerializer,
)

User = get_user_model()

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
            return self.queryset.annotate(
                duration=Sum('time_logs__duration')
            )
        return super(TaskViewSet, self).get_queryset()

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return super(TaskViewSet, self).get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(assigned_to=[self.request.user])

    @action(
        methods=['get'],
        url_path='my_task',
        detail=False,
        serializer_class=TaskListSerializer
    )
    def my_task(self, request, *args, **kwargs):
        queryset = self.queryset.filter(
            assigned_to=request.user
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=['get'],
        url_path='completed_task',
        detail=False,
        serializer_class=TaskListSerializer
    )
    def complete_task(self, request, *args, **kwargs):
        queryset = self.queryset.filter(
            status=True
        )
        serializer = self.get_serializer(
            queryset,
            many=True
        )
        return Response(serializer.data)

    @action(
        methods=['patch'],
        detail=True,
        url_path='assign_user',
        serializer_class=TaskAssignNewUserSerializer
    )
    def assign(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )
        serializer.save()
        instance.send_user_email(
            subject=f'Task with id:{instance.id} is assigned to you',
            message='Task assign to you',
            recipient=request.user.email
        )
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=True,
        url_path='update_task_status',
        serializer_class=TaskUpdateStatusSerializer
    )
    def update_status(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data
        )
        serializer.is_valid(
            raise_exception=True
        )
        serializer.save(
            status=True
        )
        user_email = request.user.email
        if user_email:
            instance.send_user_email(
                message='commented task is completed',
                subject='commented task is completed',
                recipient=user_email
            )
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=False,
    )
    def task_list_convert_pdf(self, request, *args, **kwargs):
        template_name = 'tasks/task_list.html'
        filename = 'task_list.pdf'
        context = {
            'tasks': self.get_queryset(),
        }

        return self.queryset.model.html_convert_pdf(
            request=request,
            template=template_name,
            context=context,
            filename=filename
        )

    @action(
        methods=['get'],
        detail=True,
    )
    def task_detail_convert_pdf(self, request, *args, **kwargs):
        instance = self.get_object()
        template_name = 'tasks/task_detail.html'
        filename = f'task_detail__id_{instance.id}.pdf'

        context = {
            'tasks': instance
        }
        return instance.html_convert_pdf(
            request=request,
            template=template_name,
            context=context,
            filename=filename
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
            return self.queryset.filter(
                task_id=self.kwargs.get(
                    'task__pk'
                ))
        return super(TaskCommentViewSet, self).get_queryset()

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task__pk')
        instance = serializer.save(
            owner=self.request.user,
            task_id=task_id
        )
        user_email = self.request.user.email
        instance.task.send_user_email(
            message=f'You task with id:{task_id} is commented',
            subject='Your task is commented',
            recipient=user_email
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
        duration = timedelta(
            minutes=self.request.data['duration']
        )
        serializer.save(
            task_id=self.kwargs.get('task__pk'),
            user=self.request.user,
            duration=duration
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset(
        ).filter(
            task_id=self.kwargs.get(
                'task__pk'
            ))
        serializer = self.get_serializer(
            queryset,
            many=True
        )
        return Response(serializer.data)

    @action(
        methods=['post'],
        url_path='start_timer',
        detail=False
    )
    def start_timer(self, request, *args, **kwargs):
        task_id = self.kwargs.get('task__pk')
        self.queryset.create(
            task_id=task_id,
            user=self.request.user,
            started_at=datetime.datetime.now()
        )
        return Response(status=status.HTTP_201_CREATED)

    @action(
        methods=['post'],
        url_path='stop_timer',
        detail=False
    )
    def stop_timer(self, request, *args, **kwargs):
        instance = self.queryset.filter(
            duration=None,
            user=self.request.user
        ).first()
        instance.duration = datetime.datetime.now() - instance.started_at
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
    filter_backends = [filters.OrderingFilter]
    ordering = ['-duration']

    @action(
        methods=['get'],
        detail=False,
        url_path='time_logs_month'
    )
    def time_log_month(self, request, *args, **kwargs):
        queryset = self.queryset.filter(
            user=self.request.user,
            started_at__month=TimeLog.current_month(),
        )
        return Response(
            queryset.aggregate(
                total_time=Sum('duration')
            )
        )


class AttachmentViewSet(
    ListModelMixin,
    GenericViewSet
):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    parser_classes = (MultiPartParser,)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=self.request.user
        )
        return Response(serializer.data)


class ProjectViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    GenericViewSet
):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)

    @action(
        methods=['get'],
        detail=True
    )
    def project_detail_convert_pdf(self, request, *args, **kwargs):
        instance = self.get_object()
        filename = f'project_detail__id_{instance.id}.pdf'
        template_name = 'tasks/project_detail.html'
        context = {
            'projects': instance,
            'tasks': instance.task_set.all()
        }
        return instance.task_set.model.html_convert_pdf(
            request=request,
            template=template_name,
            context=context,
            filename=filename
        )
