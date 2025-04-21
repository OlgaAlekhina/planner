import time

from celery import shared_task
from datetime import datetime, timedelta
from .models import SignupCode
import logging


logger = logging.getLogger('users')


@shared_task
def clean_codes():
	""" Задача для удаления неиспользованных кодов из БД """
	logger.info('Start of running "clean_codes" task')
	clean_date = datetime.now() - timedelta(days=1)
	logger.info(f'Run "clean_codes" task, delete {SignupCode.objects.filter(code_time__lte=clean_date)}')
	SignupCode.objects.filter(code_time__lte=clean_date).delete()


@shared_task
def test_task():
	""" Задача для проверки работы Celery """
	logger.info('Working')
