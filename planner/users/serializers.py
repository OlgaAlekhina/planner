from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class YandexAuthSerializer(serializers.Serializer):
	""" Сериализатор для OAuth токена от Яндекса """
	oauth_token = serializers.CharField(max_length=500)


class UserLoginSerializer(serializers.ModelSerializer):
	""" Сериализатор для ответа на запрос авторизации через Яндекс """
	avatar = serializers.CharField(source='userprofile.avatar')
	ya_login = serializers.CharField(source='userprofile.ya_login')
	birthday = serializers.CharField(source='userprofile.birthday')
	gender = serializers.CharField(source='userprofile.get_gender_display')

	class Meta:
		model = User
		fields = ('id', 'email', 'first_name', 'last_name', 'ya_login', 'birthday', 'gender', 'avatar')


class LoginResponseSerializer(serializers.Serializer):
	""" Сериализатор для ответа сервера при авторизации """
	user_data = UserLoginSerializer()
	user_auth_token = serializers.UUIDField()


# class ProfileSerializer(serializers.ModelSerializer):
# 	""" Сериализатор для модели UserProfile """
#
# 	class Meta:
# 		model = UserProfile
# 		fields = ('sex', 'birthday', 'ya_login', 'avatar')