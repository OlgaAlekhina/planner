import time

from celery import shared_task
from datetime import datetime, timedelta
from .models import SignupCode
import logging


logger = logging.getLogger('users')


@shared_task
def clean_codes():
	""" Задача для удаления неиспользованных кодов из БД """
	clean_date = datetime.now() - timedelta(days=1)
	SignupCode.objects.filter(code_time__lte=clean_date).delete()
	logger.info('Run "clean_codes" task')


@shared_task
def test_task():
	""" Задача для проверки работы Celery """
	time.sleep(10)
	print('Celery is working')
	logger.info('Celery is working')
