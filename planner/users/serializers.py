from rest_framework import serializers
from django.contrib.auth.models import User
from .validators import validate_password_symbols, validate_email
from .models import Group, SignupCode, GroupUser


# общие сериализаторы

class DetailSerializer(serializers.Serializer):
	""" Сериализатор для деталей ответа """
	code = serializers.CharField()
	message = serializers.CharField()


class ErrorResponseSerializer(serializers.Serializer):
	""" Сериализатор для общего ответа об ошибке """
	detail = DetailSerializer()


# сериализаторы для авторизации/регистрации и работы с данными пользователей

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
	default_groupuser_id = serializers.ReadOnlyField(source='userprofile.default_groupuser_id',
					                 help_text="Идентификатор для добавления пользователя в качестве участника события")

	class Meta:
		model = User
		fields = ('id', 'default_groupuser_id', 'email', 'first_name', 'last_name', 'nickname', 'birthday', 'gender', 'avatar', 'premium_end')
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


# сериализаторы для работы с группами

class CustomBoolField(serializers.BooleanField):
	""" Кастомное поле для проверки, является ли текущий пользователь владельцем группы """
	def to_representation(self, instance):
		current_user = self.context['request'].user
		return current_user == instance.owner

	def to_internal_value(self, data):
		return {self.field_name: data}


class GroupSerializer(serializers.ModelSerializer):
	""" Сериализатор для групп """
	is_owner = CustomBoolField(source='*', read_only=True)

	class Meta:
		model = Group
		fields = ('id', 'name', 'color', 'is_owner')

	def get_fields(self, *args, **kwargs):
		fields = super(GroupSerializer, self).get_fields(*args, **kwargs)
		request = self.context.get('request', None)
		# добавляем объект Request в поле 'is_owner'
		fields['is_owner'].contex = self.context
		# делаем поля необязательными в методе PATCH
		if request and getattr(request, 'method', None) == "PATCH":
			fields['name'].required = False
			fields['color'].required = False
		return fields


class InvitationSerializer(serializers.Serializer):
	""" Сериализатор для вступления в группу по приглашению """
	# group_id я теперь не использую, можно будет убрать по договоренности с мобильными разработчиками
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

	class Meta:
		model = GroupUser
		fields = ('id', 'user_name', 'user_role', 'user_color')

	def get_fields(self, *args, **kwargs):
		fields = super(GroupUserSerializer, self).get_fields(*args, **kwargs)
		request = self.context.get('request', None)
		# делаем поля необязательными в методе PATCH
		if request and getattr(request, 'method', None) == "PATCH":
			fields['user_name'].required = False
		return fields


class GroupUserListSerializer(serializers.Serializer):
	""" Сериализатор для группы пользователя со списком участников """
	group = GroupSerializer()
	users = serializers.ListSerializer(child=GroupUserSerializer())


class GroupUserListResponseSerializer(serializers.Serializer):
	""" Сериализатор ответа при получении всех групп пользователя со списком участников """
	detail = DetailSerializer()
	data = serializers.ListSerializer(child=GroupUserListSerializer())


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

