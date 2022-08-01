from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserListSerializer
)

User = get_user_model()

__all__ = [
    'UserViewSet'
]


class UserViewSet(
    ListModelMixin,
    GenericViewSet
):
    serializer_class = UserListSerializer
    queryset = User.objects.all()
    permission_classes = (IsAdminUser,)

    authentication_classes = [JWTAuthentication]

    @action(methods=['post'], detail=False, url_path='register', serializer_class=UserSerializer,
            permission_classes=(AllowAny,))
    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create(
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            username=serializer.validated_data['email'],
            email=serializer.validated_data['email'],
            is_superuser=False,
            is_staff=False
        )
        user.set_password(serializer.validated_data['password'])
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        })

    @action(methods=['post'], detail=False, url_path='login', serializer_class=UserCreateSerializer,
            permission_classes=(AllowAny,))
    def login(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        user = get_object_or_404(User, email=serializer.data['email'])

        if user.check_password(serializer.data['password']):
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            })

        return Response(status=status.HTTP_404_NOT_FOUND)
