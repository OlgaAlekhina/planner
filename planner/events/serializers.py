from rest_framework import serializers
from .models import Event, EventUser


class EventUserSerializer(serializers.ModelSerializer):
	""" Сериализатор для участников события """
	group_user_id = serializers.CharField(source='user.id')
	group_user_name = serializers.CharField(source='user.user_name')

	class Meta:
		model = EventUser
		fields = ('id', 'group_user_id', 'group_user_name')


class EventSerializer(serializers.ModelSerializer):
	""" Сериализатор для создания события """
	event_users = serializers.ListField(child=EventUserSerializer())

	class Meta:
		model = Event
		fields = ('id', 'title', 'location', 'start_date', 'end_date', 'start_time', 'end_time', 'event_users')