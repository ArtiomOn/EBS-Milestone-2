from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

User = get_user_model()


def auth(user):
    refresh = RefreshToken.for_user(user)
    return {
        "HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'
    }


class UserTestCase(APITestCase):

    def setUp(self) -> None:
        self.simple_user = User.objects.create(
            email='simple@test.com',
            first_name='simple_first_name',
            last_name='simple_last_name',
            username='simple@test.com',
            is_superuser=False,
            is_staff=False,
        )
        self.simple_user_password = 'simple'
        self.simple_user.set_password(self.simple_user_password)
        self.simple_user.save()
        self.simple_user_refresh = RefreshToken.for_user(self.simple_user)

        self.admin_user = User.objects.create(
            email='admin@test.com',
            first_name='admin_first_name',
            last_name='admin_last_name',
            username='admin@test.com',
            is_superuser=True,
            is_staff=True,
        )
        self.admin_user_password = 'admin'
        self.admin_user.set_password(self.admin_user_password)
        self.admin_user.save()
        self.admin_user_refresh = RefreshToken.for_user(self.admin_user)

    def test_simple_user_access_token(self):
        # Simple user get access token
        data = {
            'email': self.simple_user.email,
            'password': self.simple_user_password
        }
        response = self.client.post(path='/users/token/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_access_token(self):
        # Admin user get access token
        data = {
            'email': self.admin_user.email,
            'password': self.admin_user_password
        }
        response = self.client.post(path='/users/token/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_simple_user_refresh_token(self):
        # Simple user get refresh token
        data = {
            'refresh': str(self.simple_user_refresh)
        }
        response = self.client.post(path='/users/token/refresh/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_refresh_token(self):
        # Admin user get refresh token
        data = {
            'refresh': str(self.admin_user_refresh)
        }
        response = self.client.post(path='/users/token/refresh/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_simple_user_users_list(self):
        # Simple user get list of users
        response = self.client.get(path='/users/user/', **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_user_users_list(self):
        # Admin user get list of users
        response = self.client.get(path='/users/user/', **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_user_login_simple_user(self):
        # Unauthorized user login as simple user
        data = {
            'email': self.simple_user.email,
            'password': self.simple_user_password
        }
        response = self.client.post(path='/users/user/login/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_user_login_admin_user(self):
        # Unauthorized user login as admin user
        data = {
            'email': self.admin_user.email,
            'password': self.admin_user_password
        }
        response = self.client.post(path='/users/user/login/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_user_register_used_user_data(self):
        # Unauthorized user register new account with already used user data
        data = {
            'first_name': self.simple_user.first_name,
            'last_name': self.simple_user.last_name,
            'email': self.simple_user.email,
            'password': self.simple_user_password
        }
        response = self.client.post(path='/users/user/register/', data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_user_register_new_user_data(self):
        # Unauthorized user register new account with new user data
        data = {
            'first_name': 'test_first_name',
            'last_name': 'test_last_name',
            'email': 'test@gmail.com',
            'password': '000000'
        }
        response = self.client.post(path='/users/user/register/', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
