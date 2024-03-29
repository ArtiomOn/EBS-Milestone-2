from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


app.conf.beat_schedule = {
    # Scheduler Name
    'send-email-every-day-18-hour': {
        # Task Name (Name Specified in Decorator)
        'task': 'apps.tasks.tasks.send_email',
        # Schedule
        'schedule': crontab(hour='18', minute=0)

    }
}
app.conf.timezone = 'UTC'
