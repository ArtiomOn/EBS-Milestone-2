from rest_framework.routers import DefaultRouter

from apps.tasks.views import TaskViewSet

base_router = DefaultRouter()
base_router.register(r'task', TaskViewSet, basename='tasks')

urlpatterns = base_router.urls
