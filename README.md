# EBS-Milestone-2

## Used technologies

- [Django](https://www.djangoproject.com/)
- [Django Rest Framework](https://www.django-rest-framework.org/)
- [Swagger](https://swagger.io/docs/specification/2-0/what-is-swagger/)

## Installation

1. Install requirements `pip install -r requirements.txt`
2. Apply migrations to database `python manage.py migrate`
3. Start the project `python manage.py runserver`

## Endpoints:
### Users:
1. User access token `POST | users/token/access/`
2. User refresh token `POST | users/token/refresh/`
3. User list `GET | users/user/`
4. User register `POST | users/user/register/`
### Tasks:
1. Task list `GET | tasks/`
2. Create task `POST | tasks/`
3. All completed tasks `GET | tasks/completed_task/`
4. My own task `GET | tasks/my_task/`
5. Convert all tasks to pdf `GET | tasks/task_list_convert_pdf`
6. Task detail `GET | tasks/{id}/`
7. Delete task `DELETE | tasks/{id}/`
8. Assign new user to task `PATCH | tasks/{id}/assign_user/`
9. Convert specific task to pdf `GET | tasks/{id}/task_detail_convert_pdf/`
10. Update task status to true `GET | tasks/{id}/update_task_status/`
### Comments:
1. Comment detail `GET | tasks/{task__pk}/comments`
2. Create comment `POST | tasks/{task__pk}/comments`
### TimeLogs:
1. Timelog list `GET | timelogs/`
2. Timelogs by month `GET |  timelogs/time_logs_month/`
3. Timelog task detail `GET | tasks/{task__pk}/task_timelogs/`
4. Create task timelog `POST | tasks/{task__pk}/task_timelogs/`
5. Timelog start timer `POST | tasks/{task__pk}/task_timelogs/start_timer`
6. Timelog stop timer `POST | tasks/{task__pk}/task_timelogs/stop_timer`
### Files:
1. File list `GET | files/`
2. Create file `POST | files/`
### Projects:
1. Project list `GET | projects/`
2. Create project `POST | projects/`
3. Project detail `GET | projects/{id}/`
4. Update project `PUT & PATCH | projects/{id}/`
5. Convert project detail to pdf `GET | projects/{id}/project_detail_convert_pdf`



    