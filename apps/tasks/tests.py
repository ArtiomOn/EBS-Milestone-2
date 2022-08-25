from datetime import datetime, timedelta

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
                 project_id=3,
                 description='#1',
                 status=True
                 ),
            Task(title='#2',
                 project_id=3,
                 description='#2',
                 status=True
                 ),
            Task(title='#3',
                 project_id=3,
                 description='#3',
                 status=False
                 ),
            Task(title='#4',
                 project_id=3,
                 description='#4',
                 status=False
                 )
        ])

    def test_simple_user_list_task(self):
        # Simple user get list of tasks
        response = self.client.get(
            path='/tasks/tasks/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_list_task(self):
        # Admin user get list of tasks
        response = self.client.get(
            path='/tasks/tasks/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_user_list_task(self):
        # Unauthorized user get list of tasks
        response = self.client.get(
            path='/tasks/tasks/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_create_task(self):
        # Simple user create new task
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
        # Admin user create new task
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
        # Unauthorized user create new task
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
        # Simple user get list of all completed tasks
        response = self.client.get(
            path='/tasks/tasks/completed_task/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_completed_list_task(self):
        # Admin user get list of all completed tasks
        response = self.client.get(
            path='/tasks/tasks/completed_task/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_user_completed_list_task(self):
        # Unauthorized user get list of all completed tasks
        response = self.client.get(
            path='/tasks/tasks/completed_task/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_user_my_list_task(self):
        # Admin user get list of his own tasks
        response = self.client.get(
            path='/tasks/tasks/my_task/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_simple_user_my_list_task(self):
        # Simple user get list of his own tasks
        response = self.client.get(
            path='/tasks/tasks/my_task/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_user_my_list_task(self):
        # Unauthorized user get list of his own tasks
        response = self.client.get(
            path='/tasks/tasks/my_task/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_detail_task(self):
        # Simple user get task detail
        user_id: int = User.objects.get(email='admin@test.com').id
        task_id: int = Task.objects.first().id
        content = {
            'id': task_id,
            'title': '#1',
            'description': '#1',
            'status': True,
            'assigned_to': user_id,
            'attachment': []
        }
        response = self.client.get(
            path=f'/tasks/tasks/{task_id}/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, content)

    def test_admin_user_detail_task(self):
        # Admin user get task detail
        task_id: int = Task.objects.first().id
        response = self.client.get(
            path=f'/tasks/tasks/{task_id}/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data.get('title'),
            Task.objects.get(id=task_id).title
        )

    def test_unauthorized_user_detail_task(self):
        # Unauthorized user get task detail
        task_id: int = Task.objects.first().id
        response = self.client.get(
            path=f'/tasks/tasks/{task_id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_delete_task(self):
        # Simple user delete task
        task_id: int = Task.objects.first().id

        response = self.client.delete(
            path=f'/tasks/tasks/{task_id}/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_user_delete_task(self):
        # Admin user delete task
        task_id: int = Task.objects.first().id
        response = self.client.delete(
            path=f'/tasks/tasks/{task_id}/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthorized_user_delete_task(self):
        # Unauthorized user delete task
        task_id: int = Task.objects.first().id
        response = self.client.delete(
            path=f'/tasks/tasks/{task_id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_assign_task(self):
        # Simple user assign task to another user
        user_id: int = User.objects.first().id
        task_id: int = Task.objects.first().id

        data = {
            'assigned_to': user_id
        }
        response = self.client.patch(
            path=f'/tasks/tasks/{task_id}/assign_user/',
            data=data,
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            str(Task.objects.get(id=task_id).owner),
            User.objects.get(id=user_id).email
        )

    def test_admin_user_assign_task(self):
        # Admin user assign task to another user
        user_id: int = User.objects.first().id
        task_id: int = Task.objects.first().id

        data = {
            'assigned_to': user_id
        }
        response = self.client.patch(
            path=f'/tasks/tasks/{task_id}/assign_user/',
            data=data,
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            str(Task.objects.get(id=task_id).owner),
            User.objects.get(id=user_id).email
        )

    def test_unauthorized_user_assign_task(self):
        # Unauthorized user assign task to another user
        task_id: int = Task.objects.first().id
        data = {
            'assigned_to': 2
        }
        response = self.client.patch(
            path=f'/tasks/tasks/{task_id}/assign_user/',
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_update_status_task(self):
        # Simple user update task status to True
        task_id: int = Task.objects.first().id
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
        # Admin user update task status to True
        task_id: int = Task.objects.last().id
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
        # Unauthorized user update task status to True
        task_id: int = Task.objects.first().id
        response = self.client.get(
            f'/tasks/tasks/{task_id}/update_task_status/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# noinspection DuplicatedCode
class CommentTestCase(APITestCase):
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
                task_id=Task.objects.first().id,
                assigned_to=self.admin_user
            ),
            Comment(
                text='TEXT#2',
                task_id=Task.objects.first().id,
                assigned_to=self.admin_user
            ),
            Comment(
                text='TEXT#3',
                task_id=Task.objects.last().id,
                assigned_to=self.simple_user
            ),
            Comment(
                text='TEXT#4',
                task_id=Task.objects.last().id,
                assigned_to=self.simple_user
            )
        ])

    def test_simple_user_list_comment(self):
        # Simple user get list of comments by task id
        task_id: int = Task.objects.first().id
        response = self.client.get(
            f'/tasks/tasks/{task_id}/comments/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_list_comment(self):
        # Admin user get list of comments by task id
        task_id: int = Task.objects.last().id
        response = self.client.get(
            f'/tasks/tasks/{task_id}/comments/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_user_list_comment(self):
        # Unauthorized user get list of comments by task id
        task_id: int = Task.objects.first().id
        response = self.client.get(
            f'/tasks/tasks/{task_id}/comments/'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_create_comment(self):
        # Simple user create new comment
        task_id: int = Task.objects.first().id
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
            response.data.get('text'),
            data.get('text')
        )

    def test_admin_user_create_comment(self):
        # Admin user create new comment
        task_id: int = Task.objects.last().id
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
            response.data.get('text'),
            data.get('text')
        )

    def test_unauthorized_user_create_comment(self):
        # Unauthorized user create new comment
        task_id: int = Task.objects.first().id
        data = {
            'text': 'test_text'
        }
        response = self.client.post(
            f'/tasks/tasks/{task_id}/comments/',
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# noinspection DuplicatedCode
class TimeLogTestCase(APITestCase):
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

        self.time_log = TimeLog.objects.bulk_create([
            TimeLog(
                task_id=Task.objects.first().id,
                user=self.admin_user,
                started_at=datetime.now(),
                duration=timedelta(minutes=10)
            ),
            TimeLog(
                task_id=Task.objects.first().id,
                user=self.admin_user,
                started_at=datetime.now(),
                duration=timedelta(minutes=10)
            ),
            TimeLog(
                task_id=Task.objects.last().id,
                user=self.simple_user,
                started_at=datetime.now(),
                duration=timedelta(hours=10)
            ),
            TimeLog(
                task_id=Task.objects.last().id,
                user=self.simple_user,
                started_at=datetime.now(),
                duration=timedelta(hours=10)
            )
        ])

    def test_simple_user_list_task_timelog(self):
        # Simple user get list of all time logs by task id
        task_id: int = Task.objects.last().id
        response = self.client.get(
            f'/tasks/tasks/{task_id}/task_timelogs/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            datetime.strptime(
                response.data[0].get('duration'),
                '%H:%M:%S'
            ).minute,
            datetime.strptime(
                str(TimeLog.objects.filter(task_id=task_id).first().duration),
                '%H:%M:%S'
            ).minute
        )

    def test_admin_user_list_task_timelog(self):
        # Admin user get list of all time logs by task id
        task_id: int = Task.objects.first().id
        response = self.client.get(
            f'/tasks/tasks/{task_id}/task_timelogs/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            datetime.strptime(
                response.data[0].get('duration'),
                '%H:%M:%S'
            ).minute,
            datetime.strptime(
                str(TimeLog.objects.filter(task_id=task_id).first().duration),
                '%H:%M:%S'
            ).minute
        )

    def test_unauthorized_user_list_task_timelog(self):
        # Unauthorized user get list of all time logs by task id
        task_id: int = Task.objects.last().id
        response = self.client.get(
            f'/tasks/tasks/{task_id}/task_timelogs/',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_create_timelog(self):
        # Simple user create time log
        task_id: int = Task.objects.first().id
        data = {
            "started_at": datetime.now(),
            "duration": 10
        }
        response = self.client.post(
            f'/tasks/tasks/{task_id}/task_timelogs/',
            data=data,
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_user_create_timelog(self):
        # Admin user create time log
        task_id: int = Task.objects.last().id
        data = {
            "started_at": datetime.now(),
            "duration": 10
        }
        response = self.client.post(
            f'/tasks/tasks/{task_id}/task_timelogs/',
            data=data,
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorized_user_create_timelog(self):
        # Unauthorized user create time log
        task_id: int = Task.objects.first().id
        data = {
            "started_at": datetime.now(),
            "duration": 10
        }
        response = self.client.post(
            f'/tasks/tasks/{task_id}/task_timelogs/',
            data=data,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_start_timer_timelog(self):
        # Simple user start timer to create time log
        task_id: int = Task.objects.first().id
        response = self.client.get(
            f'/tasks/tasks/{task_id}/task_timelogs/start_timer/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_user_start_timer_timelog(self):
        # Admin user start timer to create time log
        task_id: int = Task.objects.first().id
        response = self.client.get(
            f'/tasks/tasks/{task_id}/task_timelogs/start_timer/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorized_user_start_timer_timelog(self):
        # Unauthorized user start timer to create time log
        task_id: int = Task.objects.first().id
        response = self.client.get(
            f'/tasks/tasks/{task_id}/task_timelogs/start_timer/',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_stop_timer_timelog(self):
        # Simple user stop timer to create time log
        TimeLog.objects.create(
            task_id=Task.objects.first().id,
            user=self.simple_user,
            started_at=datetime.now(),
            duration=None
        )
        task_id: int = Task.objects.first().id
        response = self.client.get(
            f'/tasks/tasks/{task_id}/task_timelogs/stop_timer/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_stop_timer_timelog(self):
        # Admin user stop timer to create time log
        TimeLog.objects.create(
            task_id=Task.objects.first().id,
            user=self.admin_user,
            started_at=datetime.now(),
            duration=None
        )
        task_id: int = Task.objects.first().id
        response = self.client.get(
            f'/tasks/tasks/{task_id}/task_timelogs/stop_timer/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_user_stop_timer_timelog(self):
        # Unauthorized user stop timer to create time log
        task_id: int = Task.objects.first().id
        response = self.client.get(
            f'/tasks/tasks/{task_id}/task_timelogs/stop_timer/',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_list_timelog(self):
        # Simple user list all time logs
        response = self.client.get(
            f'/tasks/timelogs/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_list_timelog(self):
        # Admin user list all time logs
        response = self.client.get(
            f'/tasks/timelogs/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_user_list_timelog(self):
        # Unauthorized user list all time logs
        response = self.client.get(
            f'/tasks/timelogs/',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_simple_user_list_month_timelog(self):
        # Simple user get list all time logs for month
        response = self.client.get(
            f'/tasks/timelogs/time_logs_month/',
            **auth(self.simple_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_user_list_month_timelog(self):
        # Admin user get list all time logs for month
        response = self.client.get(
            f'/tasks/timelogs/time_logs_month/',
            **auth(self.admin_user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized_user_list_month_timelog(self):
        # Unauthorized user get list all time logs for month
        response = self.client.get(
            f'/tasks/timelogs/time_logs_month/',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
