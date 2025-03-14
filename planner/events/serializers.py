from rest_framework import serializers
from .models import Event, EventMeta


class EventSerializer(serializers.ModelSerializer):
	""" Общий сериализатор для события """

	class Meta:
		model = Event
		exclude = ['author']


class EventListSerializer(serializers.ModelSerializer):
	""" Сериализатор для кратких данных события """

	class Meta:
		model = Event
		exclude = ['author', 'repeats', 'end_repeat']


class EventMetaSerializer(serializers.ModelSerializer):
	""" Сериализатор для метаданных события """
	freq = serializers.IntegerField(min_value=0, max_value=3,
									help_text='Паттерн повторений, возможные значения: 3 - для повторений по дням, 2 - по неделям,'
																		' 1 - по месяцам, 0 - по годам')
	interval = serializers.IntegerField(min_value=2, max_value=1000, required=False,
										help_text='Интервал повторений, передавать надо, только если он больше 1')
	byweekday = serializers.CharField(max_length=50, required=False,
									  help_text='Список дней недели через запятую, где 0 - понедельник, 6 - воскресенье')
	bymonthday = serializers.CharField(max_length=50, required=False,
									  help_text='Список дней месяца через запятую, например, "1, 28" - для повторов 1-ого и 28-ого числа')
	bymonth = serializers.IntegerField(min_value=1, max_value=12, help_text='Номер месяца', required=False)
	byweekno = serializers.IntegerField(min_value=1, max_value=5, help_text='Номер недели', required=False)

	class Meta:
		model = EventMeta
		exclude = ['id', 'event']

	def to_representation(self, instance):
		ret = super().to_representation(instance)
		# переводим строку, содержащую дни недели, в кортеж чисел
		if ret['byweekday']:
			ret['byweekday'] = sorted(tuple(map(int, ret['byweekday'].split(','))))
		# переводим строку, содержащую дни месяца, в кортеж чисел
		if ret['bymonthday']:
			ret['bymonthday'] = sorted(tuple(map(int, ret['bymonthday'].split(','))))
		return ret


class EventCreateSerializer(serializers.Serializer):
	""" Сериализатор для создания события """
	event_data = EventSerializer()
	repeat_pattern = EventMetaSerializer(required=False)

