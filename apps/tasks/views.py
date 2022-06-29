from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer


class TaskViewSet(GenericViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (AllowAny,)

    @action(methods=['post'], url_path='create', detail=False, serializer_class=TaskSerializer,
            permission_classes=(AllowAny,))
    def create_task(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(assign_to=self.request.user)
        return Response(serializer.data['id'], status=status.HTTP_201_CREATED)
