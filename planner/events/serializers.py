from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
	""" Сериализатор для создания события """

	class Meta:
		model = Event
		fields = ('id', 'title', 'location', 'start_date', 'end_date', 'start_time', 'end_time')