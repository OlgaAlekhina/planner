from rest_framework import serializers
from django.contrib.auth.models import User
from .validators import validate_password_symbols, validate_email, check_email
from .models import UserProfile


class DetailSerializer(serializers.Serializer):
	""" Сериализатор для деталей ответа """
	code = serializers.CharField()
	message = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
	""" Сериализатор для общего ответа об ошибке """
	detail = DetailSerializer()


class YandexAuthSerializer(serializers.Serializer):
	""" Сериализатор для OAuth токена от Яндекса """
	oauth_token = serializers.CharField(max_length=2000)


class VKAuthSerializer(serializers.Serializer):
	""" Сериализатор для входных данных при авторизации через VK ID """
	code_verifier = serializers.CharField(required=False, max_length=150)
	code = serializers.CharField(required=False, max_length=500)
	device_id = serializers.CharField(max_length=500)
	state = serializers.CharField(max_length=500)


class UserLoginSerializer(serializers.ModelSerializer):
	""" Сериализатор для ответа на запрос авторизации через Яндекс """
	avatar = serializers.CharField(source='userprofile.avatar')
	nickname = serializers.CharField(source='userprofile.nickname')
	birthday = serializers.CharField(source='userprofile.birthday', required=False)
	gender = serializers.CharField(source='userprofile.get_gender_display', required=False)

	class Meta:
		model = User
		fields = ('id', 'email', 'first_name', 'last_name', 'nickname', 'birthday', 'gender', 'avatar')
		extra_kwargs = {
						'first_name': {'required': True},
						'last_name': {'required': True},
						'email': {'required': True},
						}


class LoginDataResponseSerializer(serializers.Serializer):
	""" Сериализатор данных пользователя для ответа сервера при авторизации """
	user_data = UserLoginSerializer()
	user_auth_token = serializers.UUIDField()


class LoginResponseSerializer(serializers.Serializer):
	""" Сериализатор для ответа сервера при авторизации """
	detail = DetailSerializer()
	data = LoginDataResponseSerializer()


class MailAuthSerializer(serializers.ModelSerializer):
	""" Сериализатор для регистрации пользователя по email """
	email = serializers.CharField(max_length=50, validators=[validate_email])
	password = serializers.CharField(write_only=True, min_length=8, max_length=128, validators=[validate_password_symbols])

	class Meta:
		model = User
		fields = ('email', 'password')

# class ProfileSerializer(serializers.ModelSerializer):
# 	""" Сериализатор для модели UserProfile """
#
# 	class Meta:
# 		model = UserProfile
# 		fields = ('sex', 'birthday', 'ya_login', 'avatar')