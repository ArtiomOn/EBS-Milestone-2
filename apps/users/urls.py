from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_nested.routers import NestedSimpleRouter, DefaultRouter

from apps.users.views import UserViewSet

base_router = DefaultRouter()
base_router.register(r'user', UserViewSet, basename='users')

urlpatterns = base_router.urls

urlpatterns += [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
