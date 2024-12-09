from rest_framework import serializers
from .models import UserProfile


# serializer for UserProfile model
class ProfileSerializer(serializers.ModelSerializer):
	""" Сериализатор для модели UserProfile """

	class Meta:
		model = UserProfile
		fields = ('sex', 'birthday', 'ya_login', 'avatar')