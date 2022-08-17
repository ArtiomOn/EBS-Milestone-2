from django.conf.urls.static import static
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
    AttachmentViewSet,
    ProjectViewSet
)
from config import settings

base_router = DefaultRouter()

base_router.register(
    prefix=r'tasks',
    viewset=TaskViewSet,
    basename='tasks'
)
base_router.register(
    prefix=r'timelogs',
    viewset=TimeLogViewSet,
    basename='timelogs'
)
base_router.register(
    prefix=r'files',
    viewset=AttachmentViewSet,
    basename='files'
)
base_router.register(
    prefix=r'projects',
    viewset=ProjectViewSet,
    basename='projects'
)

nested_router = NestedSimpleRouter(
    parent_router=base_router,
    parent_prefix=r'tasks',
    lookup='task'
)
nested_router.register(
    prefix=r'comments',
    viewset=TaskCommentViewSet,
    basename='comments'
)
nested_router.register(
    prefix=r'task_timelogs',
    viewset=TaskTimeLogViewSet,
    basename='task_timelogs'
)

urlpatterns = [
    path('', include(base_router.urls)),
    path('', include(nested_router.urls)),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)
