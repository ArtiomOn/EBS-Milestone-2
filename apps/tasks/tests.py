import json

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tasks.models import Task

User = get_user_model()


def auth(user):
    refresh = RefreshToken.for_user(user)
    return {
        'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'
    }


class TaskTestCase(APITestCase):

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

        self.task = Task.objects.bulk_create([
            Task(title='#1',
                 description='#1',
                 assigned_to=self.admin_user,
                 status=True
                 ),
            Task(title='#2',
                 description='#2',
                 assigned_to=self.admin_user,
                 status=True
                 ),
            Task(title='#3',
                 description='#3',
                 assigned_to=self.simple_user,
                 status=True
                 ),
            Task(title='#4',
                 description='#4',
                 assigned_to=self.simple_user,
                 status=True
                 )
        ])

    def test_simple_user_task_list(self):
        response = self.client.get(path='/tasks/tasks/', **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_task_list(self):
        response = self.client.get(path='/tasks/tasks/', **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_user_task_list(self):
        response = self.client.get(path='/tasks/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_task_create(self):
        data = {
            'title': 'string',
            'description': 'string',
            'status': True
        }
        response = self.client.post(path='/tasks/tasks/', data=data, **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_user_task_create(self):
        data = {
            'title': 'string',
            'description': 'string',
            'status': True
        }
        response = self.client.post(path='/tasks/tasks/', data=data, **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorized_user_task_create(self):
        data = {
            'title': 'string',
            'description': 'string',
            'status': True
        }
        response = self.client.post(path='/tasks/tasks/', data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_completed_task_list(self):
        response = self.client.get(path='/tasks/tasks/completed_task/', **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_completed_task_list(self):
        response = self.client.get(path='/tasks/tasks/completed_task/', **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_user_completed_task_list(self):
        response = self.client.get(path='/tasks/tasks/completed_task/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_user_my_task_list(self):
        content = [
            {
                'id': 1,
                'title': '#1'
            },
            {
                'id': 2,
                'title': '#2'
            }
        ]
        response = self.client.get(path='/tasks/tasks/my_task/', **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), content)

    def test_simple_user_my_task_list(self):
        content = [
            {
                'id': 3,
                'title': '#3'
            },
            {
                'id': 4,
                'title': '#4'
            }
        ]
        response = self.client.get(path='/tasks/tasks/my_task/', **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), content)

    def test_unauthorized_user_my_task_list(self):
        response = self.client.get(path='/tasks/tasks/my_task/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_task_detail(self):
        content = {
            'id': 1,
            'title': '#1',
            'description': '#1',
            'status': True,
            'assigned_to': 2
        }
        response = self.client.get(path='/tasks/tasks/1/', **auth(self.simple_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), content)

    def test_admin_user_task_detail(self):
        content = {
            'id': 3,
            'title': '#3',
            'description': '#3',
            'status': True,
            'assigned_to': 1
        }
        response = self.client.get(path='/tasks/tasks/3/', **auth(self.admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), content)

    def test_unauthorized_user_task_detail(self):
        response = self.client.get(path='/tasks/tasks/1/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
