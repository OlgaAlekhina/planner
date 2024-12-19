import requests
from requests.exceptions import RequestException, HTTPError
from django.contrib.auth.models import User
from django.contrib.auth import login

from .models import UserProfile
from .serializers import (UserLoginSerializer,)


def get_or_create_user(token):
	oauth_token = token
	headers = {"Authorization": f"OAuth {oauth_token}"}
	url = "https://login.yandex.ru/info"
	try:
		response = requests.get(url, headers=headers)
		response.raise_for_status()
		response_data = response.json()
		print('response:', response.json())
		if response_data:
			email = response_data.get('default_email')
			user = User.objects.filter(email=email)
			if user:
				# получить все данные по юзеру, включая токен и группу/группы
				user_data = UserLoginSerializer(user[0]).data
				print('data: ', user_data)
				return user_data, 200
			else:
				# зарегистрировать юзера в БД и вернуть все его данные
				ya_login = response_data.get('login')
				avatar = response_data.get('default_avatar_id')
				birthday = response_data.get('birthday')
				first_name = response_data.get('first_name')
				last_name = response_data.get('last_name')
				gender = response_data.get('gender')
				if gender == 'male':
					gender = 'M'
				elif gender == 'female':
					gender = 'F'
				else:
					gender = 'N'
				user = User.objects.create_user(username=email, email=email, first_name=first_name, last_name=last_name)
				user_id = user.id
				profile = UserProfile.objects.get(user=user)
				profile.ya_login = ya_login
				# profile.birthday = birthday
				profile.gender = gender
				profile.save()
				user = User.objects.get(id=user_id)
				return UserLoginSerializer(user).data, 200
		else:
			return None


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
				"code": f"REQUEST_ERROR - {response.status_code}",
				"message": str(err)
			}
		}
		return result_data, response.status_code

