from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tasks.models import (
    Task,
    Comment,
    TimeLog
)

User = get_user_model()


def auth(user):
    refresh = RefreshToken.for_user(user)
    return {
        'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'
    }


# noinspection DuplicatedCode
class TaskTestCase(APITestCase):
    fixtures = ['task_fixtures.json', 'user_fixtures.json']

    def setUp(self) -> None:
        self.simple_user = User.objects.get(
            email='user@example.com'
        )
        self.admin_user = User.objects.get(
            email='admin@admin.com'
        )
        self.simple_user_refresh = RefreshToken.for_user(
            self.simple_user
        )
        self.admin_user_refresh = RefreshToken.for_user(
            self.admin_user
        )
        self.simple_user_task = Task.objects.get(
            title='create user'
        )
        self.admin_user_task = Task.objects.get(
            title='create admin'
        )

    def test_simple_user_list_task(self):
        # Simple user get list of tasks
        response = self.client.get(
            path='/tasks/',
            **auth(self.simple_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_admin_user_list_task(self):
        # Admin user get list of tasks
        response = self.client.get(
            path='/tasks/',
            **auth(self.admin_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_unauthorized_user_list_task(self):
        # Unauthorized user get list of tasks
        response = self.client.get(
            path='/tasks/'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_simple_user_create_task(self):
        # Simple user create new task
        data = {
            'title': 'string',
            'description': 'string',
            'status': True,
            'project': 3
        }
        response = self.client.post(
            path='/tasks/',
            data=data,
            **auth(self.simple_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_admin_user_create_task(self):
        # Admin user create new task
        data = {
            'title': 'string',
            'description': 'string',
            'status': True,
            'project': 3
        }
        response = self.client.post(
            path='/tasks/',
            data=data,
            **auth(self.admin_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_unauthorized_user_create_task(self):
        # Unauthorized user create new task
        data = {
            'title': 'string',
            'description': 'string',
            'status': True,
            'project': 3
        }
        response = self.client.post(
            path='/tasks/',
            data=data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_simple_user_completed_list_task(self):
        # Simple user get list of all completed tasks
        response = self.client.get(
            path='/tasks/completed_task/',
            **auth(self.simple_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_admin_user_completed_list_task(self):
        # Admin user get list of all completed tasks
        response = self.client.get(
            path='/tasks/completed_task/',
            **auth(self.admin_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_unauthorized_user_completed_list_task(self):
        # Unauthorized user get list of all completed tasks
        response = self.client.get(
            path='/tasks/completed_task/'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_admin_user_my_list_task(self):
        # Admin user get list of his own tasks
        response = self.client.get(
            path='/tasks/my_task/',
            **auth(self.admin_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_simple_user_my_list_task(self):
        # Simple user get list of his own tasks
        response = self.client.get(
            path='/tasks/my_task/',
            **auth(self.simple_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_unauthorized_user_my_list_task(self):
        # Unauthorized user get list of his own tasks
        response = self.client.get(
            path='/tasks/my_task/'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_simple_user_detail_task(self):
        # Simple user get task detail
        task_id: int = self.simple_user_task.id
        response = self.client.get(
            path=f'/tasks/{task_id}/',
            **auth(self.simple_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.data.get('title'),
            Task.objects.get(id=task_id).title
        )

    def test_admin_user_detail_task(self):
        # Admin user get task detail
        task_id: int = self.admin_user_task.id
        response = self.client.get(
            path=f'/tasks/{task_id}/',
            **auth(self.admin_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.data.get('title'),
            Task.objects.get(id=task_id).title
        )

    def test_unauthorized_user_detail_task(self):
        # Unauthorized user get task detail
        task_id: int = self.simple_user_task.id
        response = self.client.get(
            path=f'/tasks/{task_id}/'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_simple_user_delete_task(self):
        # Simple user delete task
        task_id: int = self.simple_user_task.id

        response = self.client.delete(
            path=f'/tasks/{task_id}/',
            **auth(self.simple_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

    def test_admin_user_delete_task(self):
        # Admin user delete task
        task_id: int = self.admin_user_task.id
        response = self.client.delete(
            path=f'/tasks/{task_id}/',
            **auth(self.admin_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

    def test_unauthorized_user_delete_task(self):
        # Unauthorized user delete task
        task_id: int = self.simple_user_task.id
        response = self.client.delete(
            path=f'/tasks/{task_id}/'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_simple_user_assign_task(self):
        # Simple user assign task to another user
        user_id: int = self.simple_user.id
        task_id: int = self.simple_user_task.id

        data = {
            'assigned_to': [user_id]
        }
        response = self.client.patch(
            path=f'/tasks/{task_id}/assign_user/',
            data=data,
            **auth(self.simple_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_admin_user_assign_task(self):
        # Admin user assign task to another user
        user_id: int = self.admin_user.id
        task_id: int = self.admin_user_task.id

        data = {
            'assigned_to': [user_id]
        }
        response = self.client.patch(
            path=f'/tasks/{task_id}/assign_user/',
            data=data,
            **auth(self.admin_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_unauthorized_user_assign_task(self):
        # Unauthorized user assign task to another user
        user_id: int = self.simple_user.id
        task_id: int = self.simple_user_task.id
        data = {
            'assigned_to': [user_id]
        }
        response = self.client.patch(
            path=f'/tasks/{task_id}/assign_user/',
            data=data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_simple_user_update_status_task(self):
        # Simple user update task status to True
        task_id: int = self.simple_user_task.id
        response = self.client.get(
            f'/tasks/{task_id}/update_task_status/',
            **auth(self.simple_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            Task.objects.get(id=task_id).status,
            True
        )

    def test_admin_user_update_status_task(self):
        # Admin user update task status to True
        task_id: int = self.admin_user_task.id
        response = self.client.get(
            f'/tasks/{task_id}/update_task_status/',
            **auth(self.admin_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            Task.objects.get(id=task_id).status,
            True
        )

    def test_unauthorized_user_update_status_task(self):
        # Unauthorized user update task status to True
        task_id: int = self.simple_user_task.id
        response = self.client.get(
            f'/tasks/{task_id}/update_task_status/'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


# noinspection DuplicatedCode
class CommentTestCase(APITestCase):
    fixtures = ['task_fixtures.json', 'user_fixtures.json']

    def setUp(self) -> None:
        self.simple_user = User.objects.get(
            email='user@example.com'
        )
        self.admin_user = User.objects.get(
            email='admin@admin.com'
        )
        self.simple_user_refresh = RefreshToken.for_user(
            self.simple_user
        )
        self.admin_user_refresh = RefreshToken.for_user(
            self.admin_user
        )
        self.simple_user_task = Task.objects.get(
            title='create user'
        )
        self.admin_user_task = Task.objects.get(
            title='create admin'
        )
        self.simple_user_comment = Comment.objects.get(
            text='comment_one'
        )
        self.admin_user_comment = Comment.objects.get(
            text='comment_two'
        )

    def test_simple_user_list_comment(self):
        # Simple user get list of comments by task id
        task_id: int = self.simple_user_task.id
        response = self.client.get(
            f'/tasks/{task_id}/comments/',
            **auth(self.simple_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_admin_user_list_comment(self):
        # Admin user get list of comments by task id
        task_id: int = self.admin_user_task.id
        response = self.client.get(
            f'/tasks/{task_id}/comments/',
            **auth(self.admin_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_unauthorized_user_list_comment(self):
        # Unauthorized user get list of comments by task id
        task_id: int = self.simple_user_task.id
        response = self.client.get(
            f'/tasks/{task_id}/comments/'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_simple_user_create_comment(self):
        # Simple user create new comment
        task_id: int = self.simple_user_task.id
        data = {
            'text': 'test_text#1'
        }
        response = self.client.post(
            f'/tasks/{task_id}/comments/',
            data=data,
            **auth(self.simple_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(
            response.data.get('text'),
            data.get('text')
        )

    def test_admin_user_create_comment(self):
        # Admin user create new comment
        task_id: int = self.admin_user_task.id
        data = {
            'text': 'test_text#4'
        }
        response = self.client.post(
            f'/tasks/{task_id}/comments/',
            data=data,
            **auth(self.admin_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(
            response.data.get('text'),
            data.get('text')
        )

    def test_unauthorized_user_create_comment(self):
        # Unauthorized user create new comment
        task_id: int = self.simple_user_task.id
        data = {
            'text': 'test_text'
        }
        response = self.client.post(
            f'/tasks/{task_id}/comments/',
            data=data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


# noinspection DuplicatedCode
class TimeLogTestCase(APITestCase):
    fixtures = ['task_fixtures.json', 'user_fixtures.json']

    def setUp(self) -> None:
        self.simple_user = User.objects.get(
            email='user@example.com'
        )
        self.admin_user = User.objects.get(
            email='admin@admin.com'
        )
        self.simple_user_refresh = RefreshToken.for_user(
            self.simple_user
        )
        self.admin_user_refresh = RefreshToken.for_user(
            self.admin_user
        )
        self.simple_user_task = Task.objects.get(
            title='create user'
        )
        self.admin_user_task = Task.objects.get(
            title='create admin'
        )
        self.simple_user_timelog = TimeLog.objects.get(
            user_id=39
        )
        self.admin_user_timelog = TimeLog.objects.get(
            user_id=1
        )

    def test_simple_user_list_task_timelog(self):
        # Simple user get list of all time logs by task id
        task_id: int = self.simple_user_task.id
        response = self.client.get(
            f'/tasks/{task_id}/task_timelogs/',
            **auth(self.simple_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_admin_user_list_task_timelog(self):
        # Admin user get list of all time logs by task id
        task_id: int = self.admin_user_task.id
        response = self.client.get(
            f'/tasks/{task_id}/task_timelogs/',
            **auth(self.admin_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_unauthorized_user_list_task_timelog(self):
        # Unauthorized user get list of all time logs by task id
        task_id: int = self.simple_user_task.id
        response = self.client.get(
            f'/tasks/{task_id}/task_timelogs/',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_simple_user_create_timelog(self):
        # Simple user create time log
        task_id: int = self.simple_user_task.id
        data = {
            "started_at": datetime.now(),
            "duration": 10
        }
        response = self.client.post(
            f'/tasks/{task_id}/task_timelogs/',
            data=data,
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_user_create_timelog(self):
        # Admin user create time log
        task_id: int = self.admin_user_task.id
        data = {
            "started_at": datetime.now(),
            "duration": 10
        }
        response = self.client.post(
            f'/tasks/{task_id}/task_timelogs/',
            data=data,
            **auth(self.admin_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_unauthorized_user_create_timelog(self):
        # Unauthorized user create time log
        task_id: int = self.simple_user_task.id
        data = {
            "started_at": datetime.now(),
            "duration": 10
        }
        response = self.client.post(
            f'/tasks/{task_id}/task_timelogs/',
            data=data,
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_simple_user_start_timer_timelog(self):
        # Simple user start timer to create time log
        task_id: int = self.simple_user_task.id
        response = self.client.post(
            f'/tasks/{task_id}/task_timelogs/start_timer/',
            **auth(self.simple_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_admin_user_start_timer_timelog(self):
        # Admin user start timer to create time log
        task_id: int = self.admin_user_task.id
        response = self.client.post(
            f'/tasks/{task_id}/task_timelogs/start_timer/',
            **auth(self.admin_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_unauthorized_user_start_timer_timelog(self):
        # Unauthorized user start timer to create time log
        task_id: int = self.simple_user_task.id
        response = self.client.post(
            f'/tasks/{task_id}/task_timelogs/start_timer/',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_simple_user_stop_timer_timelog(self):
        # Simple user stop timer to create time log
        task_id: int = self.simple_user_task.id
        self.client.post(
            f'/tasks/{task_id}/task_timelogs/start_timer/',
            **auth(self.simple_user)
        )
        response = self.client.post(
            f'/tasks/{task_id}/task_timelogs/stop_timer/',
            **auth(self.simple_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_admin_user_stop_timer_timelog(self):
        # Admin user stop timer to create time log
        task_id: int = self.admin_user_task.id
        self.client.post(
            f'/tasks/{task_id}/task_timelogs/start_timer/',
            **auth(self.admin_user)
        )
        response = self.client.post(
            f'/tasks/{task_id}/task_timelogs/stop_timer/',
            **auth(self.admin_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_unauthorized_user_stop_timer_timelog(self):
        # Unauthorized user stop timer to create time log
        task_id: int = self.simple_user_task.id
        response = self.client.post(
            f'/tasks/{task_id}/task_timelogs/stop_timer/',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_simple_user_list_timelog(self):
        # Simple user list all time logs
        response = self.client.get(
            f'/timelogs/',
            **auth(self.simple_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_admin_user_list_timelog(self):
        # Admin user list all time logs
        response = self.client.get(
            f'/timelogs/',
            **auth(self.admin_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_unauthorized_user_list_timelog(self):
        # Unauthorized user list all time logs
        response = self.client.get(
            f'/timelogs/',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_simple_user_list_month_timelog(self):
        # Simple user get list all time logs for month
        response = self.client.get(
            f'/timelogs/time_logs_month/',
            **auth(self.simple_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_admin_user_list_month_timelog(self):
        # Admin user get list all time logs for month
        response = self.client.get(
            f'/timelogs/time_logs_month/',
            **auth(self.admin_user)
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_unauthorized_user_list_month_timelog(self):
        # Unauthorized user get list all time logs for month
        response = self.client.get(
            f'/timelogs/time_logs_month/',
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
