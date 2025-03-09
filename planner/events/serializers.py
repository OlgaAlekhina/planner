from rest_framework import serializers
from .models import Event, EventMeta


class EventSerializer(serializers.ModelSerializer):
	""" Сериализатор для создания события """

	class Meta:
		model = Event
		fields = ('id', 'title', 'location', 'start_date', 'end_date', 'start_time', 'end_time', 'users')


# class CustomByweekdayField(serializers.CharField):
# 	""" Кастомное поле для перевода значения byweekday из строки в кортеж """
# 	def to_representation(self, instance):
# 		return tuple(map(int, instance.split(',')))


class EventMetaSerializer(serializers.ModelSerializer):
	""" Сериализатор для метаданных события """
	# byweekday = CustomByweekdayField(read_only=True)

	class Meta:
		model = EventMeta
		fields = ('freq', 'interval', 'byweekday', 'bymonthday')

	def to_representation(self, instance):
		ret = super().to_representation(instance)
		# переводим строку, содержащую дни недели, в кортеж чисел
		if ret['byweekday']:
			ret['byweekday'] = tuple(map(int, ret['byweekday'].split(',')))
		return ret