from rest_framework import serializers
from django.contrib.auth.models import User
from .validators import validate_password_symbols, validate_email
from .models import SignupCode


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
	""" Сериализатор для ответа на запрос авторизации """
	avatar = serializers.CharField(source='userprofile.avatar')
	nickname = serializers.CharField(source='userprofile.nickname')
	birthday = serializers.CharField(source='userprofile.birthday', required=False)
	gender = serializers.CharField(source='userprofile.get_gender_display', required=False)
	premium_end = serializers.DateField(source='userprofile.premium_end', required=False)
	default_groupuser_id = serializers.IntegerField(source='userprofile.default_groupuser_id', help_text="Идентификатор"
															 " для добавления пользователя в качестве участника события")

	class Meta:
		model = User
		fields = ('id', 'default_groupuser_id', 'email', 'first_name', 'last_name', 'nickname', 'birthday', 'gender',
				  'avatar', 'premium_end')
		extra_kwargs = {
						'first_name': {'required': True},
						'last_name': {'required': True},
						'email': {'required': True},
						}


class UserUpdateSerializer(serializers.ModelSerializer):
	""" Сериализатор для редактирования данных пользователя """

	class Meta:
		model = User
		fields = ('first_name',)


class LoginDataResponseSerializer(serializers.Serializer):
	""" Сериализатор данных пользователя для ответа сервера при авторизации """
	user_data = UserLoginSerializer()
	user_auth_token = serializers.UUIDField()


class UserResponseSerializer(serializers.Serializer):
	""" Сериализатор данных пользователя для ответа сервера без токена """
	detail = DetailSerializer()
	data = UserLoginSerializer()


class LoginResponseSerializer(serializers.Serializer):
	""" Сериализатор для ответа сервера при авторизации """
	detail = DetailSerializer()
	data = LoginDataResponseSerializer()


class MailAuthSerializer(serializers.ModelSerializer):
	""" Сериализатор для авторизации пользователя по email """
	email = serializers.CharField(max_length=50, validators=[validate_email])
	password = serializers.CharField(write_only=True, min_length=8, max_length=128, validators=[validate_password_symbols])

	class Meta:
		model = User
		fields = ('email', 'password')


class SignupSerializer(serializers.ModelSerializer):
	""" Сериализатор для регистрации пользователя по email """
	email = serializers.CharField(max_length=50, validators=[validate_email])
	password = serializers.CharField(write_only=True, min_length=8, max_length=128, validators=[validate_password_symbols])

	class Meta:
		model = User
		fields = ('email', 'password')


class ResetPasswordSerializer(serializers.ModelSerializer):
	""" Сериализатор для восстановления пароля пользователя по email """
	email = serializers.CharField(max_length=50, validators=[validate_email])

	class Meta:
		model = User
		fields = ('email',)


class CodeSerializer(serializers.ModelSerializer):
	""" Сериализатор для верификации кода """
	code = serializers.IntegerField(max_value=9999)

	class Meta:
		model = SignupCode
		fields = ('code', )


class UserIDSerializer(serializers.Serializer):
	""" Сериализатор для ID пользователя """
	user_id = serializers.IntegerField()


class SignupResponseSerializer(serializers.Serializer):
	""" Сериализатор для ответа сервера при регистрации пользователя по email """
	detail = DetailSerializer()
	data = UserIDSerializer()

