from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
)
from rest_framework_nested.routers import DefaultRouter

from apps.users.views import UserViewSet

base_router = DefaultRouter()
base_router.register(
    prefix=r'user',
    viewset=UserViewSet,
    basename='users'
)

urlpatterns = base_router.urls

urlpatterns += [
    path(
        'token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path(
        'token/access/',
        TokenObtainPairView.as_view(),
        name='token_access'
    )
]
