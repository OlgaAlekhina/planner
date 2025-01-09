import requests
from django.conf import settings
from requests.exceptions import RequestException, HTTPError
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import (UserLoginSerializer,)
from rest_framework.authtoken.models import Token


client_id = settings.VK_CLIENT_ID


def update_or_create(email, first_name, last_name, nickname, gender, birthday, avatar):
	if gender in ('male', 2):
		gender = 'M'
	elif gender in ('female', 1):
		gender = 'F'
	else:
		gender = 'N'
	if 'http' not in avatar:
		avatar = f'https://avatars.yandex.net/get-yapic/{avatar}/islands-75'
	user, created = User.objects.update_or_create(
		email=email,
		defaults={"first_name": first_name, "last_name": last_name},
		create_defaults={"username": email, "email": email, "first_name": first_name, "last_name": last_name},
	)
	user_id = user.id
	profile = UserProfile.objects.get(user=user)
	profile.nickname = nickname
	if birthday:
		profile.birthday = birthday
	profile.gender = gender
	profile.avatar = avatar
	profile.save()
	user = User.objects.get(id=user_id)
	token = Token.objects.get(user=user)
	user_data = UserLoginSerializer(user).data
	result = {"user_data": user_data, "user_auth_token": token.key}
	return result


def get_user_from_yandex(token):
	headers = {"Authorization": f"OAuth {token}"}
	url = "https://login.yandex.ru/info"
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
		gender = response_data.get('gender')
		user_data = update_or_create(email, first_name, last_name, nickname, gender, birthday, avatar)
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
				"code": "REQUEST_ERROR - 500",
				"message": str(err)
			}
		}
		return result_data, 500


def get_user_from_vk(code_verifier, code, device_id, state):
	url = "https://id.vk.com/oauth2/auth"
	headers = {"Content-Type": "application/x-www-form-urlencoded"}
	data = {"grant_type": "authorization_code", "code_verifier": code_verifier, "code": code, "client_id": client_id,
			"device_id": device_id, "state": state}
	try:
		response = requests.post(url, headers=headers, json=data)
		response.raise_for_status()
		response_data = response.json()
		access_token = response_data.get("access_token")
		url = "https://id.vk.com/oauth2/user_info"
		headers = {"Content-Type": "application/x-www-form-urlencoded"}
		data = {"client_id": client_id, "access_token": access_token}
		response = requests.post(url, headers=headers, json=data)
		response.raise_for_status()
		response_data = response.json().get('user')
		email = response_data.get('email')
		nickname = email.split('@')[0]
		avatar = response_data.get('avatar')
		birthday = response_data.get('birthday')
		first_name = response_data.get('first_name')
		last_name = response_data.get('last_name')
		gender = response_data.get('sex')
		if gender == 2:
			gender = 'M'
		elif gender == 1:
			gender = 'F'
		else:
			gender = 'N'
		user, created = User.objects.update_or_create(
			email=email,
			defaults={"first_name": first_name, "last_name": last_name},
			create_defaults={"username": email, "email": email, "first_name": first_name, "last_name": last_name},
		)
		user_id = user.id
		profile = UserProfile.objects.get(user=user)
		profile.nickname = nickname
		if birthday:
			profile.birthday = birthday
		if avatar:
			profile.avatar = f'https://avatars.yandex.net/get-yapic/{avatar}/islands-75'
		profile.gender = gender
		profile.save()
		user = User.objects.get(id=user_id)
		return UserLoginSerializer(user).data, 200
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
				"code": "REQUEST_ERROR - 500",
				"message": str(err)
			}
		}
		return result_data, 500


