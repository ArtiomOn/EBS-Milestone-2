import json

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tasks.models import (
    Task,
    Comment,
    TimeLog
)

from datetime import datetime, timedelta

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
                 status=False
                 ),
            Task(title='#4',
                 description='#4',
                 assigned_to=self.simple_user,
                 status=False
                 )
        ])

        self.comment = Comment.objects.bulk_create([
            Comment(
                text='TEXT#1',
                task_id=1,
                assigned_to=self.admin_user
            ),
            Comment(
                text='TEXT#2',
                task_id=2,
                assigned_to=self.admin_user
            ),
            Comment(
                text='TEXT#3',
                task_id=3,
                assigned_to=self.simple_user
            ),
            Comment(
                text='TEXT#4',
                task_id=3,
                assigned_to=self.simple_user
            )
        ])
        self.time_log = TimeLog.objects.bulk_create([
            TimeLog(
                task_id=1,
                user=self.admin_user,
                started_at=datetime.now(),
                duration=timedelta(minutes=10)
            ),
            TimeLog(
                task_id=2,
                user=self.admin_user,
                started_at=datetime.now(),
                duration=timedelta(minutes=10)
            ),
            TimeLog(
                task_id=3,
                user=self.simple_user,
                started_at=datetime.now(),
                duration=timedelta(hours=10)
            ),
            TimeLog(
                task_id=4,
                user=self.simple_user,
                started_at=datetime.now(),
                duration=timedelta(hours=10)
            )
        ])

    def test_simple_user_list_task(self):
        response = self.client.get(
            path='/tasks/tasks/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_list_task(self):
        response = self.client.get(
            path='/tasks/tasks/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_user_list_task(self):
        response = self.client.get(
            path='/tasks/tasks/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_create_task(self):
        data = {
            'title': 'string',
            'description': 'string',
            'status': True
        }
        response = self.client.post(
            path='/tasks/tasks/',
            data=data,
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_user_create_task(self):
        data = {
            'title': 'string',
            'description': 'string',
            'status': True
        }
        response = self.client.post(
            path='/tasks/tasks/',
            data=data,
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorized_user_create_task(self):
        data = {
            'title': 'string',
            'description': 'string',
            'status': True
        }
        response = self.client.post(
            path='/tasks/tasks/',
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_completed_list_task(self):
        response = self.client.get(
            path='/tasks/tasks/completed_task/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_completed_list_task(self):
        response = self.client.get(
            path='/tasks/tasks/completed_task/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_user_completed_list_task(self):
        response = self.client.get(
            path='/tasks/tasks/completed_task/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_user_my_list_task(self):
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
        response = self.client.get(
            path='/tasks/tasks/my_task/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), content)

    def test_simple_user_my_list_task(self):
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
        response = self.client.get(
            path='/tasks/tasks/my_task/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), content)

    def test_unauthorized_user_my_list_task(self):
        response = self.client.get(
            path='/tasks/tasks/my_task/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_detail_task(self):
        task_id: int = 1
        content = {
            'id': 1,
            'title': '#1',
            'description': '#1',
            'status': True,
            'assigned_to': 2
        }
        response = self.client.get(
            path=f'/tasks/tasks/{task_id}/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), content)

    def test_admin_user_detail_task(self):
        task_id: int = 3
        response = self.client.get(
            path=f'/tasks/tasks/{task_id}/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            json.loads(response.content).get('title'),
            Task.objects.get(id=task_id).title
        )

    def test_unauthorized_user_detail_task(self):
        task_id: int = 1
        response = self.client.get(
            path=f'/tasks/tasks/{task_id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_delete_task(self):
        task_id: int = 1
        response = self.client.delete(
            path=f'/tasks/tasks/{task_id}/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_user_delete_task(self):
        task_id: int = 1
        response = self.client.delete(
            path=f'/tasks/tasks/{task_id}/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthorized_user_delete_task(self):
        task_id: int = 1
        response = self.client.delete(
            path=f'/tasks/tasks/{task_id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_list_comment(self):
        task_id: int = 1
        response = self.client.get(
            f'/tasks/tasks/{task_id}/comments/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_list_comment(self):
        task_id: int = 4
        response = self.client.get(
            f'/tasks/tasks/{task_id}/comments/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_user_list_comment(self):
        task_id: int = 1
        response = self.client.get(
            f'/tasks/tasks/{task_id}/comments/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_create_comment(self):
        task_id: int = 1
        data = {
            'text': 'test_text#1'
        }
        response = self.client.post(
            f'/tasks/tasks/{task_id}/comments/',
            data=data,
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            json.loads(response.content).get('text'),
            data.get('text')
        )

    def test_admin_user_create_comment(self):
        task_id: int = 4
        data = {
            'text': 'test_text#4'
        }
        response = self.client.post(
            f'/tasks/tasks/{task_id}/comments/',
            data=data,
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            json.loads(response.content).get('text'),
            data.get('text')
        )

    def test_unauthorized_user_create_comment(self):
        task_id: int = 1
        data = {
            'text': 'test_text'
        }
        response = self.client.post(
            f'/tasks/tasks/{task_id}/comments/',
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_list_timelog(self):
        task_id: int = 4
        response = self.client.get(
            f'/tasks/tasks/{task_id}/task_timelogs/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            datetime.strptime(
                json.loads(response.content)[0].get('duration'),
                '%H:%M:%S'
            ).minute,
            datetime.strptime(
                str(TimeLog.objects.get(task_id=task_id).duration),
                '%H:%M:%S'
            ).minute
        )

    def test_admin_user_list_timelog(self):
        task_id: int = 2
        response = self.client.get(
            f'/tasks/tasks/{task_id}/task_timelogs/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            datetime.strptime(
                json.loads(response.content)[0].get('duration'),
                '%H:%M:%S'
            ).minute,
            datetime.strptime(
                str(TimeLog.objects.get(task_id=task_id).duration),
                '%H:%M:%S'
            ).minute
        )

    def test_unauthorized_user_list_timelog(self):
        task_id: int = 3
        response = self.client.get(
            f'/tasks/tasks/{task_id}/task_timelogs/',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_assign_task(self):
        user_id: int = 1
        task_id: int = 1
        data = {
            'assigned_to': 1
        }
        response = self.client.patch(
            path=f'/tasks/tasks/{task_id}/assign_user/',
            data=data,
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            str(Task.objects.get(id=task_id).assigned_to),
            User.objects.get(id=user_id).email
        )

    def test_admin_user_assign_task(self):
        user_id: int = 2
        task_id: int = 3
        data = {
            'assigned_to': 2
        }
        response = self.client.patch(
            path=f'/tasks/tasks/{task_id}/assign_user/',
            data=data,
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            str(Task.objects.get(id=task_id).assigned_to),
            User.objects.get(id=user_id).email
        )

    def test_unauthorized_user_assign_task(self):
        task_id: int = 1
        data = {
            'assigned_to': 2
        }
        response = self.client.patch(
            path=f'/tasks/tasks/{task_id}/assign_user/',
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_update_status_task(self):
        task_id: int = 3
        response = self.client.get(
            f'/tasks/tasks/{task_id}/update_task_status/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Task.objects.get(id=task_id).status,
            True
        )

    def test_admin_user_update_status_task(self):
        task_id: int = 4
        response = self.client.get(
            f'/tasks/tasks/{task_id}/update_task_status/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Task.objects.get(id=task_id).status,
            True
        )

    def test_unauthorized_user_update_status_task(self):
        task_id: int = 4
        response = self.client.get(
            f'/tasks/tasks/{task_id}/update_task_status/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
