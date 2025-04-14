import logging
import os
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'planner.settings')

logger = logging.getLogger(__name__)

app = Celery('planner')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'cleaning_codes_every_monday_8am': {
        'task': 'users.tasks.clean_codes',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
    },
}

app.conf.beat_schedule = {
    'test_every_5_minutes': {
        'task': 'users.tasks.test_task',
        'schedule': timedelta(seconds=20),
    },
}

@app.task
def test():
    logger.info("It is working!")
    return True
