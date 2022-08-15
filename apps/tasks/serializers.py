from django.template.defaultfilters import filesizeformat

from rest_framework import serializers

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


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'assigned_to': {'read_only': True},
        }


class TaskListSerializer(serializers.ModelSerializer):
    duration = serializers.DurationField(read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'duration', 'attachment')


class TaskAssignNewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('assigned_to',)


class TaskUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('status',)
        extra_kwargs = {
            'status': {'read_only': True}
        }


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {
            'task': {'read_only': True},
            'assigned_to': {'read_only': True}
        }


class TimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = '__all__'


class TimeLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = '__all__'

        extra_kwargs = {
            'user': {'read_only': True},
            'task': {'read_only': True}
        }


class TimeLogUserDetailSerializer(serializers.ModelSerializer):
    total_time = serializers.DurationField(read_only=True)

    class Meta:
        model = TimeLog
        fields = ('id', 'total_time', 'started_at', 'duration', 'attachment')
        extra_kwargs = {
            'started_at': {'read_only': True}
        }


class AttachmentSerializer(serializers.ModelSerializer):
    file_size = serializers.SerializerMethodField()

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


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
