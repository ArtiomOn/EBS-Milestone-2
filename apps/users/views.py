from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import UserSerializer

User = get_user_model()

__all__ = [
    'UserViewSet'
]


class UserViewSet(
    ListModelMixin,
    GenericViewSet
):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    authentication_classes = [JWTAuthentication]

    @action(
        methods=['post'],
        detail=False,
        url_path='register',
        serializer_class=UserSerializer,
        permission_classes=(AllowAny,)
    )
    def register(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        user: User = serializer.save(
            username=serializer.validated_data['email']
        )

        user.set_password(serializer.validated_data['password'])
        user.save()
        refresh: RefreshToken = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        })
