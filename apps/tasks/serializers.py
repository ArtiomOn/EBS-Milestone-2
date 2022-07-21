from rest_framework.serializers import (
    ModelSerializer,
    DurationField
)

from apps.tasks.models import (
    Task,
    Comment,
    TimeLog
)


class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'assigned_to': {'read_only': True}
        }


class TaskListSerializer(ModelSerializer):
    duration = DurationField(read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'duration')


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
        fields = ('id', 'total_time', 'started_at')
        extra_kwargs = {
            'started_at': {'read_only': True}
        }
