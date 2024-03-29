from datetime import timedelta, datetime

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
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

from apps.tasks.models import (
    Task,
    Comment,
    TimeLog,
    Attachment,
    Project,
    TaskQuerySet,
    ProjectQuerySet,
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
    queryset: TaskQuerySet = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = [JWTAuthentication]
    filter_backends = [filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['title']

    def get_queryset(self) -> QuerySet:
        queryset = super(TaskViewSet, self).get_queryset()
        if self.action == 'list':
            return queryset.with_duration()
        return queryset

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
        instance: Task = self.get_object()
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
        instance: Task = self.get_object()
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
        user_email: str = request.user.email
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
        template_name: str = 'tasks/task_list.html'
        filename: str = 'task_list.pdf'
        context: dict = {
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
        instance: Task = self.get_object()
        template_name: str = 'tasks/task_detail.html'
        filename: str = f'task_detail__id_{instance.id}.pdf'

        context: dict = {
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

    def list(self, request, *args, **kwargs):
        task_id: int = self.kwargs.get(
            'task__pk'
        )
        queryset = self.queryset.filter(
            task_id=task_id
        )
        serializer = self.get_serializer(
            queryset,
            many=True
        )
        return Response(serializer.data)

    def perform_create(self, serializer):
        task_id: int = self.kwargs.get(
            'task__pk'
        )
        instance: Comment = serializer.save(
            owner=self.request.user,
            task_id=task_id
        )
        user_email: str = self.request.user.email
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
        task_id: int = self.kwargs.get(
            'task__pk'
        )
        duration: timedelta = timedelta(
            minutes=self.request.data['duration']
        )
        serializer.save(
            task_id=task_id,
            user=self.request.user,
            duration=duration,
            is_started=True,
            is_stopped=True,
        )

    def list(self, request, *args, **kwargs):
        task_id: int = self.kwargs.get(
            'task__pk'
        )
        queryset = self.get_queryset(
        ).filter(
            task_id=task_id
        )
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
        task_id: int = self.kwargs.get(
            'task__pk'
        )
        existing_unstopped_timelog: TimeLog = self.queryset.filter(
            task_id=task_id,
            user=self.request.user,
            is_started=True,
            is_stopped=False,
        ).last()
        if not existing_unstopped_timelog:
            self.queryset.create(
                task_id=task_id,
                user=self.request.user,
                started_at=datetime.now(),
                is_started=True,
                is_stopped=False,
            )
            return Response(status=status.HTTP_201_CREATED)
        else:
            raise NotFound('You have some unstopped tasks')

    @action(
        methods=['post'],
        url_path='stop_timer',
        detail=False
    )
    def stop_timer(self, request, *args, **kwargs):
        task_id: int = self.kwargs.get(
            'task__pk'
        )
        instance: TimeLog = self.queryset.filter(
            task_id=task_id,
            is_started=True,
            is_stopped=False,
            duration=None,
            user=self.request.user
        ).first()
        if instance:
            instance.duration = datetime.now() - instance.started_at
            instance.is_stopped = True
            instance.is_started = False
            instance.save()
            return Response(status=status.HTTP_200_OK)
        else:
            raise NotFound("You don't have started time logs")


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
            started_at__month=datetime.now().strftime('%m'),
        )
        return Response(
            queryset.with_total_time()
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
    queryset: ProjectQuerySet = Project.objects.all()
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
