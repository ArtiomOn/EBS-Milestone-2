from django.urls import path, include
from rest_framework_nested.routers import NestedSimpleRouter, DefaultRouter

from apps.tasks.views import TaskViewSet, TaskCommentViewSet


base_router = DefaultRouter()
base_router.register(r'tasks', TaskViewSet, basename='tasks')

nested_router = NestedSimpleRouter(base_router, r'tasks', lookup='task')
nested_router.register(r'comments', TaskCommentViewSet)

urlpatterns = [
    path('', include(base_router.urls)),
    path('', include(nested_router.urls)),
]
