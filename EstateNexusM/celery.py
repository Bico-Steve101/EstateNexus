from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EstateNexusM.settings')

app = Celery('EstateNexusM')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.update(timezone='Africa/Nairobi')

app.conf.beat_schedule = {
    'send-scheduled-messages-every-minute': {
        'task': 'User.tasks.send_scheduled_messages',
        'schedule': crontab(),
    },
}

CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'


if settings.USE_TZ:
    CELERY_ENABLE_UTC = True
    CELERY_TIMEZONE = settings.TIME_ZONE


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
