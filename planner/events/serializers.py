from rest_framework import serializers
from .models import Event, EventMeta


class EventSerializer(serializers.ModelSerializer):
	""" Сериализатор для создания события """

	class Meta:
		model = Event
		fields = ('id', 'title', 'location', 'start_date', 'end_date', 'start_time', 'end_time', 'users')


class EventMetaSerializer(serializers.ModelSerializer):
	""" Сериализатор для метаданных события """

	class Meta:
		model = EventMeta
		exclude = ('id', 'event')