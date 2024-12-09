import requests
from requests.exceptions import RequestException, HTTPError
from django.contrib.auth.models import User
from django.contrib.auth import login

from .models import UserProfile
from .serializers import (UserLoginSerializer,)


def get_or_create_user(token):
	# email = token
	# user = User.objects.filter(email=token)
	# if user:
	# 	print('1')
	# 	# получить все данные по юзеру, включая токен и группу/группы
	# 	data = UserLoginSerializer(user[0]).data
	# 	print('data: ', data)
	# 	return data
	# else:
	# 	print('2')
	# 	# зарегистрировать юзера в БД и вернуть все его данные
	# 	ya_login = 'login'
	# 	birthday = '2000-02-20'
	# 	first_name = 'Vasya'
	# 	last_name = 'Pupkin'
	# 	sex = ''
	# 	user = User.objects.create_user(username=email, email=email, first_name=first_name, last_name=last_name)
	# 	print('user: ', user)
	# 	# login(request, user)
	# 	profile = UserProfile.objects.get(user=user)
	# 	print('profile: ', profile)
	# 	profile.ya_login = ya_login
	# 	profile.birthday = birthday
	# 	profile.sex = sex
	# 	profile.save()
	# 	return 'success!!!'
	oauth_token = token
	headers = {"Authorization:": f"OAuth {oauth_token}"}
	url = "https://login.yandex.ru/info"
	try:
		response = requests.get(url, headers=headers)
		response.raise_for_status()
		response_data = response.json().get('data', [])
		if response_data:
			email = response_data.get('default_email')
			user = User.objects.filter(email=email)
			if user:
				# получить все данные по юзеру, включая токен и группу/группы
				user_data = UserLoginSerializer(user[0]).data
				print('data: ', user_data)
			else:
				# зарегистрировать юзера в БД и вернуть все его данные
				ya_login = response_data.get('login')
				avatar = response_data.get('default_avatar_id')
				birthday = response_data.get('birthday')
				first_name = response_data.get('first_name')
				last_name = response_data.get('last_name')
				sex = response_data.get('sex')
				user = User.objects.create_user(username=email, email=email, first_name=first_name, last_name=last_name)
				profile = UserProfile.objects.get(user=user)
				profile.ya_login = ya_login
				profile.birthday = birthday
				profile.sex = sex
				profile.save()


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

