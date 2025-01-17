import os

import requests
from requests.exceptions import RequestException, HTTPError
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import (UserLoginSerializer,)
from rest_framework.authtoken.models import Token
from dotenv import load_dotenv

load_dotenv()


client_id = os.getenv('VK_CLIENT_ID')


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
				"code": f"REQUEST_ERROR - {response.status_code}" if response else 'REQUEST_ERROR - 500',
				"message": str(err)
			}
		}
		return result_data, response.status_code if response else 500


def get_user_from_vk(code_verifier, code, device_id, state):
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
	print('data:', data)
	try:
		response = requests.post(url_1, headers=headers, data=data)
		print('response: ', response.text)
		print(response.request.body)
		response.raise_for_status()
		response_data = response.json()
		access_token = response_data.get("access_token")
		if not access_token:
			return {'detail': {'code': '400_BAD_REQUEST', 'message': response.json()}}, 400
		# access_token = '12345'
		data = {"client_id": client_id, "access_token": access_token}
		response = requests.post(url_2, headers=headers, data=data)
		print('response2: ', response.json())
		response.raise_for_status()
		response_data = response.json().get('user')
		if not response_data:
			return {'detail': {'code': '400_BAD_REQUEST', 'message': response.json()}}, 400
		# email = response_data.get('email')
		# nickname = email.split('@')[0]
		# avatar = response_data.get('avatar')
		# birthday = response_data.get('birthday')
		# first_name = response_data.get('first_name')
		# last_name = response_data.get('last_name')
		# gender = response_data.get('sex')
		# user_data = update_or_create(email, first_name, last_name, nickname, gender, birthday, avatar)
		# return user_data, 200
		return response.json(), 200
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
				"code": f"REQUEST_ERROR - {response.status_code}" if response else 'REQUEST_ERROR - 500',
				"message": str(err)
			}
		}
		return result_data, response.status_code if response else 500


