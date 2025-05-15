import random
import string
from random import randint
from datetime import datetime, date
import requests
from requests.exceptions import RequestException, HTTPError
from django.contrib.auth.models import User
from .models import UserProfile, SignupCode, Group, GroupUser
from .serializers import UserLoginSerializer
from rest_framework.authtoken.models import Token
from django.conf import settings
from .tasks import send_letter

client_id = settings.VK_CLIENT_ID


def convert_date(birthday: str, date_format='%d.%m.%Y') -> date | str:
	if '-' not in birthday:
		return datetime.strptime(birthday, date_format).date()
	return birthday


def get_user(email: str, password: str) -> tuple[dict, int]:
	"""
	получает данные пользователя из БД
	возвращает данные пользователя и токен авторизации
	если у пользователя нет пароля (он регистрировался через соцсети), высылает код подтверждения на почту
	"""
	user = User.objects.filter(email__iexact=email, is_active=True)
	# если не найдено активных пользователей с данным email адресом
	if not user:
		return {"detail": {"code": "HTTP_403_FORBIDDEN", "message": "Пользователь не зарегистрирован в приложении"}}, 403

	user = user[0]
	# если в БД нет пароля, значит, пользователь регистрировался через соцсети
	# генерируем код подтверждения и высылаем на почту (через асинхронные задачи Celery)
	if not user.password:
		code = SignupCode.objects.create(code=randint(1000, 9999), user=user)
		send_letter.delay(email, code.code, 'signup', 'signup_code.html')
		# сохраняем переданный пароль и делаем профиль неактивным до подтверждения кода
		user.is_active = False
		user.set_password(password)
		user.save()
		return {"detail": {"code": "HTTP_401_UNAUTHORIZED", "message": "Выслан код подтверждения на электронную почту"},
				"data": {"user_id": user.id}}, 401

	# если пароль не совпадает с записанным в БД
	if not user.check_password(password):
		return {"detail": {"code": "HTTP_403_FORBIDDEN", "message": "Неправильный пароль"}}, 403

	# при успешно пройденных проверках получаем данные пользователя и токен авторизации
	token = Token.objects.get(user=user)
	user_data = UserLoginSerializer(user).data
	result = {"detail": {"code": "HTTP_200_OK", "message": "Авторизация прошла успешно"},
			  "data": {"user_data": user_data, "user_auth_token": token.key}}
	return result, 200


def create_user(email: str, password: str) -> tuple[dict, int]:
	"""
	создает нового пользователя в БД, но делает его неактивным до подтверждения кода
	высылает код подтверждения на почту (через асинхронные задачи Celery)
	"""
	user = User.objects.create_user(username=email, email=email, password=password)
	user.is_active = False
	user.save()

	code = SignupCode.objects.create(code=randint(1000, 9999), user=user)
	send_letter.delay(email, code.code, 'signup', 'signup_code.html')

	return {"detail": {"code": "HTTP_201_CREATED", "message": "Пользователь зарегистрирован. На электронную почту выслан "
															  "код подтверждения."}, "data": {"user_id": user.id}}, 201


def send_password(email: str) -> tuple[dict, int]:
	"""
	проверяет, есть ли пользователь с таким email в БД
	устанавливает новый пароль (случайно сгенерированный из 8 символов) и высылает его на почту
	"""
	user = User.objects.filter(email__iexact=email, is_active=True).first()
	if not user:
		return {"detail": {"code": "HTTP_403_FORBIDDEN", "message": "Пользователь с таким email адресом не "
																					"зарегистрирован в приложении"}}, 403
	new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
	user.set_password(new_password)
	user.save()
	# посылаем пароль на почту через асинхронные задачи Celery
	send_letter.delay(email, new_password, 'reset', 'reset_password.html')
	return {"detail": {"code": "HTTP_200_OK", "message": "Новый пароль успешно отправлен пользователю"}}, 200


def get_or_create_user(email: str, first_name: str, last_name: str, nickname: str, gender: str, birthday: str,
					   avatar: str) -> dict:
	"""
	создает нового пользователя или получает его данные из БД
	используется для авторизации через Яндекс и ВК
	возвращает данные пользователя и токен авторизации
	"""
	user, created = User.objects.get_or_create(
		email__iexact=email,
		defaults={"username": email, "email": email, "first_name": first_name, "last_name": last_name}
	)
	user_id = user.id
	user.is_active = True
	user.save()

	# создаем дефолтную группу и ее участника, если они отсутствуют
	group, group_created = Group.objects.get_or_create(owner=user, default=True,
												defaults={'name': 'default_group', 'color': 'default_color'})
	if group_created:
		GroupUser.objects.get_or_create(user=user, group=group, defaults={'user_name': 'me'})

	# если пользователь только что создан, добавляем его данные в таблицу UserProfile
	if created:
		if gender in ('male', 2):
			gender = 'M'
		elif gender in ('female', 1):
			gender = 'F'
		else:
			gender = 'N'
		if 'http' not in avatar:
			avatar = f'https://avatars.yandex.net/get-yapic/{avatar}/islands-75'
		profile = UserProfile.objects.get(user=user)
		profile.nickname = nickname
		if birthday:
			profile.birthday = convert_date(birthday)
		profile.gender = gender
		profile.avatar = avatar
		profile.save()
		user = User.objects.get(id=user_id)

	token = Token.objects.get(user=user)
	user_data = UserLoginSerializer(user).data
	result = {"user_data": user_data, "user_auth_token": token.key}
	return result


def get_user_from_yandex(token: str) -> tuple[dict, int]:
	"""
	получает данные пользователя из Яндекса
	создает нового пользователя или обновляет его данные в БД
	возвращает данные пользователя и токен авторизации
	"""
	headers = {"Authorization": f"OAuth {token}"}
	url = "https://login.yandex.ru/info"
	# делаем запрос в Яндекс с токеном авторизации для получения данных пользователя
	try:
		response = requests.get(url, headers=headers)
		response.raise_for_status()
		response_data = response.json()
		email = response_data.get('default_email')
		nickname = response_data.get('login')
		avatar = response_data.get('default_avatar_id')
		birthday = response_data.get('birthday')
		first_name = response_data.get('first_name')
		last_name = response_data.get('last_name')
		gender = response_data.get('sex')
		# получаем пользователя из БД, а при его отсутствии создаем нового
		user_data = get_or_create_user(email, first_name, last_name, nickname, gender, birthday, avatar)
		return user_data, 200

	except HTTPError as http_err:
		result_data = {
			"detail": {
				"code": f"HTTP_ERROR - {response.status_code}",
				"message": str(http_err)
			}
		}
		return result_data, response.status_code
	except RequestException as err:
		result_data = {
			"detail": {
				"code": f"REQUEST_ERROR - {err.response.status_code}" if err.response else 'REQUEST_ERROR - 500',
				"message": str(err)
			}
		}
		return result_data, err.response.status_code if err.response else 500


def get_user_from_vk(code_verifier: str, code: str, device_id: str, state: str) -> tuple[dict, int]:
	"""
	получает данные пользователя из ВК
	создает нового пользователя или обновляет его данные в БД
	возвращает данные пользователя и токен авторизации
	"""
	url_1 = "https://id.vk.com/oauth2/auth"
	url_2 = "https://id.vk.com/oauth2/user_info"
	headers = {"content-type": "application/x-www-form-urlencoded"}
	data = {
			"grant_type": "authorization_code",
			"code_verifier": code_verifier,
			"code": code,
			"client_id": client_id,
			"device_id": device_id,
			"state": state,
			"redirect_uri": f"vk{client_id}://vk.com/blank.html"
	}
	try:
		response = requests.post(url_1, headers=headers, data=data)
		response.raise_for_status()
		response_data = response.json()
		access_token = response_data.get("access_token")
		if not access_token:
			return {'detail': {'code': '400_BAD_REQUEST', 'message': response.json()}}, 400
		data = {"client_id": client_id, "access_token": access_token}
		response = requests.post(url_2, headers=headers, data=data)
		response.raise_for_status()
		response_data = response.json().get('user')
		if not response_data:
			return {'detail': {'code': '400_BAD_REQUEST', 'message': response.json()}}, 400
		email = response_data.get('email')
		nickname = email.split('@')[0]
		avatar = response_data.get('avatar')
		birthday = response_data.get('birthday')
		first_name = response_data.get('first_name')
		last_name = response_data.get('last_name')
		gender = response_data.get('sex')
		user_data = get_or_create_user(email, first_name, last_name, nickname, gender, birthday, avatar)
		return user_data, 200
	except HTTPError as http_err:
		result_data = {
			"detail": {
				"code": f"HTTP_ERROR - {response.status_code}",
				"message": str(http_err)
			}
		}
		return result_data, response.status_code
	except RequestException as err:
		result_data = {
			"detail": {
				"code": f"REQUEST_ERROR - {err.response.status_code}" if err.response else 'REQUEST_ERROR - 500',
				"message": str(err)
			}
		}
		return result_data, err.response.status_code if err.response else 500


