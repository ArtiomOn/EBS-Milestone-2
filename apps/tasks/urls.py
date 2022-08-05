from django.urls import path, include

from rest_framework_nested.routers import (
    NestedSimpleRouter,
    DefaultRouter
)

from apps.tasks.views import (
    TaskViewSet,
    TaskCommentViewSet,
    TaskTimeLogViewSet,
    TimeLogViewSet,
    FileViewSet,
)


base_router = DefaultRouter()
base_router.register(r'tasks', TaskViewSet, basename='tasks')
base_router.register(r'timelogs', TimeLogViewSet, basename='timelogs')
base_router.register(r'files', FileViewSet, basename='files')

nested_router = NestedSimpleRouter(base_router, r'tasks', lookup='task')
nested_router.register(r'comments', TaskCommentViewSet, basename='comments')
nested_router.register(r'task_timelogs', TaskTimeLogViewSet, basename='task_timelogs')

urlpatterns = [
    path('', include(base_router.urls)),
    path('', include(nested_router.urls)),
]
