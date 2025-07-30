from rest_framework import serializers
from .models import Group, GroupUser
from .users_serializers import DetailSerializer


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
	default_groupuser_id = serializers.SerializerMethodField()

	class Meta:
		model = GroupUser
		fields = ('id', 'default_groupuser_id', 'user_name', 'user_role', 'user_color')

	def get_default_groupuser_id(self, obj):
		user = obj.user
		default_groupuser = GroupUser.objects.filter(user=user, group__default=True).first()
		if default_groupuser:
			return default_groupuser.id
		return None

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




