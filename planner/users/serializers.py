from rest_framework import serializers
from django.contrib.auth.models import User
from .validators import validate_password_symbols, validate_email
from .models import Group, SignupCode, GroupUser


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


class GroupSerializer(serializers.ModelSerializer):
	""" Сериализатор для создания групп """
	is_owner = serializers.SerializerMethodField()

	class Meta:
		model = Group
		fields = ('id', 'name', 'color', 'is_owner')

	# чтобы сделать поле "name" необязательным в методе PATCH
	def get_fields(self, *args, **kwargs):
		fields = super(GroupSerializer, self).get_fields(*args, **kwargs)
		request = self.context.get('request', None)
		if request and getattr(request, 'method', None) == "PATCH":
			fields['name'].required = False
			fields['color'].required = False
		return fields

	# определяет, является ли текущий пользователь владельцем группы
	def get_is_owner(self, obj):
		current_user = self.context['request'].user
		return current_user == obj.owner


class InvitationSerializer(serializers.Serializer):
	""" Сериализатор для вступления в группу по приглашению """
	group_id = serializers.IntegerField()
	user_id = serializers.IntegerField()


class GroupResponseSerializer(serializers.Serializer):
	""" Сериализатор ответа при создании групп """
	detail = DetailSerializer()
	data = GroupSerializer()


class GroupListResponseSerializer(serializers.Serializer):
	""" Сериализатор ответа при получении всех групп пользователя """
	detail = DetailSerializer()
	data = serializers.ListSerializer(child=GroupSerializer())


class GroupUserSerializer(serializers.ModelSerializer):
	""" Сериализатор для участников группы """
	id = serializers.IntegerField(source='user.id', read_only=True)

	class Meta:
		model = GroupUser
		fields = ('id', 'user_name', 'user_role', 'user_color')


class GroupUserResponseSerializer(serializers.Serializer):
	""" Сериализатор ответа при создании групп """
	detail = DetailSerializer()
	data = GroupUserSerializer()


class GroupUsersResponseSerializer(serializers.Serializer):
	""" Сериализатор ответа при получении участников группы """
	detail = DetailSerializer()
	data = serializers.ListSerializer(child=GroupUserSerializer())


class CodeSerializer(serializers.ModelSerializer):
	""" Сериализатор для верификации кода """
	code = serializers.IntegerField(max_value=9999)

	class Meta:
		model = SignupCode
		fields = ('code', )

