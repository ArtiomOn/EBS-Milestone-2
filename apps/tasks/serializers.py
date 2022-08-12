from django.template.defaultfilters import filesizeformat

from rest_framework.serializers import (
    ModelSerializer,
    DurationField,
    SerializerMethodField
)

from apps.tasks.models import (
    Task,
    Comment,
    TimeLog,
    Attachment,
    Project
)

__all__ = [
    'TaskSerializer',
    'TaskListSerializer',
    'TaskAssignNewUserSerializer',
    'TaskUpdateStatusSerializer',
    'CommentSerializer',
    'TimeLogSerializer',
    'TimeLogCreateSerializer',
    'TimeLogUserDetailSerializer',
    'AttachmentSerializer',
    'ProjectSerializer'
]


class TaskSerializer(ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'assigned_to': {'read_only': True},
        }


class TaskListSerializer(ModelSerializer):
    duration = DurationField(read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'duration', 'attachment')


class TaskAssignNewUserSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = ('assigned_to',)


class TaskUpdateStatusSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = ('status',)
        extra_kwargs = {
            'status': {'read_only': True}
        }


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {
            'task': {'read_only': True},
            'assigned_to': {'read_only': True}
        }


class TimeLogSerializer(ModelSerializer):
    class Meta:
        model = TimeLog
        fields = '__all__'


class TimeLogCreateSerializer(ModelSerializer):
    class Meta:
        model = TimeLog
        fields = '__all__'

        extra_kwargs = {
            'user': {'read_only': True},
            'task': {'read_only': True}
        }


class TimeLogUserDetailSerializer(ModelSerializer):
    total_time = DurationField(read_only=True)

    class Meta:
        model = TimeLog
        fields = ('id', 'total_time', 'started_at', 'duration', 'attachment')
        extra_kwargs = {
            'started_at': {'read_only': True}
        }


class AttachmentSerializer(ModelSerializer):
    file_size = SerializerMethodField()

    def get_file_size(self, object):
        return filesizeformat(object.file_size)

    class Meta:
        model = Attachment
        fields = '__all__'

        extra_kwargs = {
            'user': {'read_only': True},
            'extension': {'read_only': True},
            'file_size': {'read_only': True}
        }


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
