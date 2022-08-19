from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
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
        queryset = self.queryset.filter(status=True)
        serializer = self.get_serializer(queryset, many=True)
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
        instance.assigned_to.set = serializer.validated_data['assigned_to']
        user_email = Task.objects.filter(
            id=instance.id
        ).select_related(
            'assigned_to'
        ).values_list(
            'assigned_to__email',
            flat=True
        )
        Task.send_user_email(
            subject=f'Task with id:{instance.id} is assigned to you',
            message='Task assign to you',
            recipient=user_email
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
        serializer.is_valid(raise_exception=True)
        serializer.save(status=True)
        user_email = set(Comment.objects.select_related(
            'task__assigned_to'
        ).filter(
            task_id=instance.id
        ).values_list(
            'assigned_to__email',
            flat=True
        ))
        if user_email:
            Task.send_user_email(
                message='commented task is completed',
                subject='commented task is completed',
                recipient=user_email
            )
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def task_list_convert_pdf(self, request, *args, **kwargs):
        template_name = 'tasks/task_list.html'
        pdf_name = 'E:/EBS/EBS-Milestone-2/media/pdf/task_list.pdf'
        task_queryset = Task.objects.all()
        comment_queryset = Comment.objects.all()
        timelog_queryset = TimeLog.objects.all()
        context = {
            'tasks': task_queryset,
            'comments': comment_queryset,
            'timelogs': timelog_queryset
        }
        return Task.html_convert_pdf(
            template=template_name,
            output_path=pdf_name,
            context=context
        )

    @action(
        methods=['get'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def task_detail_convert_pdf(self, request, *args, **kwargs):
        instance = self.get_object()
        template_name = 'tasks/task_detail.html'
        pdf_name = f'E:/EBS/EBS-Milestone-2/media/pdf/task_detail__id_{instance.id}.pdf'
        task_queryset = Task.objects.filter(
            id=instance.id
        )
        comment_queryset = Comment.objects.filter(
            task_id=instance.id
        )
        timelog_queryset = TimeLog.objects.filter(
            task_id=instance.id
        )
        context = {
            'tasks': task_queryset,
            'comments': comment_queryset,
            'timelogs': timelog_queryset
        }
        return Task.html_convert_pdf(
            template=template_name,
            output_path=pdf_name,
            context=context
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
        serializer.save(
            assigned_to=self.request.user,
            task_id=task_id
        )
        user_email = Task.objects.select_related(
            'assigned_to'
        ).filter(
            id=task_id
        ).values_list(
            'assigned_to__email',
            flat=True
        )
        Task.send_user_email(
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
        methods=['get'],
        url_path='start_timer',
        detail=False
    )
    def start_timer(self, request, *args, **kwargs):
        task_id = get_object_or_404(
            self.kwargs.get('task__pk')
        )
        TimeLog.objects.user_start_timer(
            task_id=task_id,
            user=request.user
        )
        return Response(status=status.HTTP_201_CREATED)

    @action(
        methods=['get'],
        url_path='stop_timer',
        detail=False
    )
    def stop_timer(self, request, *args, **kwargs):
        TimeLog.objects.user_stop_timer(
            user=request.user
        )
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
        return self.filter_queryset(
            self.queryset.order_by(
                '-duration'
            ))[:5]

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
        serializer = self.get_serializer(
            queryset,
            many=True
        )
        serializer.total_time = queryset.aggregate(
            Sum('duration')
        )
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
        serializer = self.get_serializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(
            user=self.request.user
        )
        return Response(
            self.get_serializer(
                instance=instance
            ).data)


class ProjectViewSet(
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
        pdf_name = f'E:/EBS/EBS-Milestone-2/media/pdf/project_detail__id_{instance.id}.pdf'
        template_name = 'tasks/project_detail.html'
        instance_project = self.get_queryset(
        ).filter(
            id=instance.id
        )
        instance_tasks = Task.objects.filter(
            project_id=instance.id
        )
        instance_comments = Comment.objects.filter(
            task__project=instance
        )
        instance_timelogs = TimeLog.objects.filter(
            task__project=instance
        )
        context = {
            'projects': instance_project,
            'tasks': instance_tasks,
            'comments': instance_comments,
            'timelogs': instance_timelogs,
        }
        return Task.html_convert_pdf(
            template=template_name,
            output_path=pdf_name,
            context=context
        )
