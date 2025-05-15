import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'planner.settings')

app = Celery('planner')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'cleaning_codes_every_monday_8am': {
        'task': 'users.tasks.clean_codes',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
    },

    # 'test_every_200_seconds': {
    #     'task': 'users.tasks.test_task',
    #     'schedule': timedelta(hours=12),
    # },
}


