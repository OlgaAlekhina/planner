from celery import shared_task
from datetime import datetime, timedelta
from .models import SignupCode
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import logging


logger = logging.getLogger('users')


@shared_task
def clean_codes():
	""" Удаляет неиспользованные коды регистрации из БД каждый понедельник """
	logger.info('Start of running "clean_codes" task')
	clean_date = datetime.now() - timedelta(days=1)
	logger.info(f'Run "clean_codes" task, delete {SignupCode.objects.filter(code_time__lte=clean_date)}')
	SignupCode.objects.filter(code_time__lte=clean_date).delete()


@shared_task
def send_letter(email: str, data: int | str, subject: str, template: str) -> None:
	""" Посылает письмо при регистрации или восстановлении пароля пользователя """
	if subject == 'signup':
		subject = 'Подтверждение авторизации/регистрации в приложении Family Planner'
	elif subject == 'reset':
		subject = 'Восстановление пароля в приложении Family Planner'
	msg = EmailMultiAlternatives(
		subject=subject,
		from_email='olga-olechka-5@yandex.ru',
		to=[email, ]
	)
	html_content = render_to_string(
		f'{template}',
		{'data': data}
	)
	msg.attach_alternative(html_content, "text/html")
	msg.send()
	logger.info('Letter was sent to user')
