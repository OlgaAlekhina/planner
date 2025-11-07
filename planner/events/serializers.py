from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from .models import Event, EventMeta, EventUser
from users.users_serializers import DetailSerializer
from users.models import GroupUser


class EventAuthorBoolField(serializers.BooleanField):
	""" Кастомное поле для проверки, является ли текущий пользователь создателем события """
	def to_representation(self, instance):
		current_user = self.context['request'].user
		return current_user == instance.author

	def to_internal_value(self, data):
		return {self.field_name: data}


class EventUserCreateSerializer(serializers.ModelSerializer):
	""" Сериализатор для добавления/изменения участника события """
	user_id = serializers.IntegerField(source='groupuser_id')

	class Meta:
		model = EventUser
		fields = ['user_id', 'left']


class EventUserSerializer(serializers.ModelSerializer):
	""" Сериализатор для получения участника события """
	user_id = serializers.SerializerMethodField()

	class Meta:
		model = EventUser
		fields = ['user_id', 'left']

	def get_user_id(self, obj):
		# для авторизованного пользователя выводится его дефолтный id, для остальных - id группы
		user_id = obj.groupuser_id
		current_user = self.context.get('request').user
		current_groupuser_ids = [user.id for user in current_user.group_users.all()]
		current_default_groupuser_id = current_user.group_users.filter(group__default=True).first().id
		return current_default_groupuser_id if user_id in current_groupuser_ids else user_id


class EventSerializer(serializers.ModelSerializer):
	"""
	Общий сериализатор для вывода основных данных события. Используется только для Response, так как в списке участников
	события ID текущего пользователя заменяется на его default groupuser ID.
	"""
	is_creator = EventAuthorBoolField(source='*', read_only=True)
	users = EventUserSerializer(many=True, source='eventuser_set')

	class Meta:
		model = Event
		exclude = ['author']

	def get_fields(self, *args, **kwargs):
		fields = super(EventSerializer, self).get_fields(*args, **kwargs)
		# добавляем объект Request в поле 'is_creator'
		fields['is_creator'].contex = self.context
		return fields


class EventMetaSerializer(serializers.ModelSerializer):
	""" Сериализатор для метаданных события """
	freq = serializers.IntegerField(min_value=0, max_value=3, help_text='Паттерн повторений, возможные значения: 3 - для'
													' повторений по дням, 2 - по неделям, 1 - по месяцам, 0 - по годам')
	interval = serializers.IntegerField(min_value=1, max_value=1000, required=False, help_text='Интервал повторений, где'
														     ' 1 означает, что повторяется каждый день (неделю и т.д.)')
	byweekday = serializers.CharField(max_length=50, required=False, allow_null=True, help_text='Список дней недели через '
																		'запятую, где 0 - понедельник, 6 - воскресенье')
	bymonthday = serializers.CharField(max_length=50, required=False, allow_null=True, help_text='Список дней месяца через '
														'запятую, например, "1, 28" - для повторов 1-ого и 28-ого числа')
	bymonth = serializers.IntegerField(min_value=1, max_value=12, allow_null=True, help_text='Номер месяца', required=False)
	#byweekno = serializers.IntegerField(min_value=1, max_value=6, help_text='Номер недели', required=False)

	class Meta:
		model = EventMeta
		exclude = ['id', 'event', 'byweekno']

	def to_representation(self, instance):
		ret = super().to_representation(instance)
		# переводим строку, содержащую дни недели, в кортеж чисел
		if ret['byweekday']:
			ret['byweekday'] = sorted(tuple(map(int, ret['byweekday'].split(','))))
		# переводим строку, содержащую дни месяца, в кортеж чисел
		if ret['bymonthday']:
			ret['bymonthday'] = sorted(tuple(map(int, ret['bymonthday'].split(','))))
		return ret


class EventMetaResponseSerializer(serializers.ModelSerializer):
	""" Сериализатор для метаданных события для Response """

	class Meta:
		model = EventMeta
		exclude = ['id', 'event', 'byweekno']


class EventDataSerializer(serializers.ModelSerializer):
	""" Сериализатор для записи основных данных события """
	is_creator = EventAuthorBoolField(source='*', read_only=True)
	users = EventUserCreateSerializer(many=True)

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


class EventCreateSerializer(serializers.Serializer):
	""" Общий сериализатор для создания и редактирования события вместе с метаданными """
	event_data = EventDataSerializer()
	repeat_pattern = EventMetaSerializer(required=False)


class EventMetaDataSerializer(serializers.Serializer):
	""" Сериализатор ответа сервера для получения данных и метаданных события """
	event_data = EventSerializer()
	repeat_pattern = EventMetaSerializer()


class EventResponseSerializer(serializers.Serializer):
	""" Сериализатор ответа сервера для получения события """
	detail = DetailSerializer()
	data = EventMetaDataSerializer()


class EventCreateResponseSerializer(serializers.Serializer):
	""" Сериализатор ответа сервера при создании и редактировании события """
	detail = DetailSerializer()
	data = EventCreateSerializer()


class EventListResponseSerializer(serializers.Serializer):
	""" Сериализатор для ответа сервера в list методе """
	detail = DetailSerializer()
	data = serializers.ListSerializer(child=EventMetaDataSerializer())

