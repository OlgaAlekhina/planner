from rest_framework import serializers
from .models import Event, EventMeta
from users.serializers import DetailSerializer


class EventSerializer(serializers.ModelSerializer):
	""" Общий сериализатор для события """

	class Meta:
		model = Event
		exclude = ['author']
		extra_kwargs = {
			'start_time': {
				'help_text': 'Время начала события в формате 06:30:00'
			},
			'end_time': {
				'help_text': 'Время завершения события в формате 07:30:00'
			}
		}

	def get_fields(self, *args, **kwargs):
		fields = super(EventSerializer, self).get_fields(*args, **kwargs)
		request = self.context.get('request', None)
		# делаем поля необязательными в методе PATCH
		if request and getattr(request, 'method', None) == "PATCH":
			fields['title'].required = False
			fields['start_date'].required = False
			fields['end_date'].required = False
			fields['users'].required = False
		return fields


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
	interval = serializers.IntegerField(min_value=1, max_value=1000, required=False,
										help_text='Интервал повторений, где 1 означает, что повторяется каждый день (неделю и т.д.)')
	byweekday = serializers.CharField(max_length=50, required=False,
									  help_text='Список дней недели через запятую, где 0 - понедельник, 6 - воскресенье')
	bymonthday = serializers.CharField(max_length=50, required=False,
									  help_text='Список дней месяца через запятую, например, "1, 28" - для повторов 1-ого и 28-ого числа')
	bymonth = serializers.IntegerField(min_value=1, max_value=12, help_text='Номер месяца', required=False)
	byweekno = serializers.IntegerField(min_value=1, max_value=6, help_text='Номер недели', required=False)

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


class EventResponseSerializer(serializers.Serializer):
	""" Сериализатор ответа сервера для получения события """
	detail = DetailSerializer()
	data = EventCreateSerializer()

