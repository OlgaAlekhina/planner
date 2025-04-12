from datetime import datetime, time, timedelta
from dateutil.parser import parse
from django.core.exceptions import ValidationError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Event, EventMeta, CanceledEvent
from .serializers import EventSerializer, EventMetaSerializer, EventCreateSerializer, EventListSerializer, \
	EventResponseSerializer
from users.serializers import ErrorResponseSerializer
from django.db.models import Q
from .services import get_dates
from django.core.cache import cache
from planner.permissions import EventPermission
import logging


logger = logging.getLogger('events')


class EventViewSet(viewsets.ModelViewSet):
	""" Эндпоинты для работы с событиями """
	queryset = Event.objects.all()
	http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
	parser_classes = (JSONParser, MultiPartParser)
	permission_classes = [IsAuthenticated, EventPermission]

	def get_serializer_class(self):
		if self.action in ('create', 'partial_update'):
			return EventCreateSerializer
		else:
			return EventSerializer

	@swagger_auto_schema(
		responses={
			201: openapi.Response(description="Успешное создание события", schema=EventResponseSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"error": "string"}})
		},
		operation_summary="Создание нового события",
		operation_description="Создает новое событие в календаре.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.\n"
							  "Если событие повторяется, надо передать данные о повторах в поле 'repeat_pattern'.\n\n"
							  "Пока реализованы следующие паттерны повторов событий:\n"
							  "1) По дням - через сколько дней повторяется событие: надо передать параметры freq=3 и int (например, int=1 - "
							  "повторяется каждый день, int=5 - повторяется раз в 5 дней;\n"
							  "2) По неделям - через сколько недель повторяется событие и в какие дни недели: надо передать параметры "
							  "freq=2, int (через сколько недель) и byweekday - в какой день недели (или дни), например, freq=2, int=2, byweekday='1,4' "
							  "означает, что событие повторяется через неделю по вторникам и пятницам;\n"
							  "3) По месяцам - через сколько месяцев повторяется и в какие дни месяца: надо передать парметры freq=1, "
							  "int (через сколько месяцев) и bymonthday (какого числа), например, freq=1, int=1, bymonthday='5' "
							  "означает, что событие повторяется каждый месяц 5-ого числа;\n"
							  "4) По годам - через сколько лет повторяется событие и в какую дату: надо передать параметры freq=0, int (через сколько лет), "
							  "bymonthday (в какой день месяца) и bymonth (в какой месяц), например, freq=0, int=2, bymonthday='8', bymonth=2 "
							  "означает, что событие повторяется 8 февраля через год."
	)
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			user = request.user
			event_data = serializer.validated_data.get('event_data')
			event_meta = serializer.validated_data.get('repeat_pattern')
			users = event_data.pop('users', None)
			# создаем новое событие в БД
			event = Event.objects.create(author=user, **event_data)
			logger.info(f"Создано событие: id = {event.id}, title = {event.title}")
			# добавляем участников события вручную
			if users:
				for user in users:
					event.users.add(user)
			# если нет списка участников, добавляем только текущего пользователя
			else:
				event.users.add(user)
			response = {
				'event_data': EventSerializer(event, context={'request': request}).data
			}
			# если были получены метаданные, делаем запись в таблице
			if event_meta:
				meta = EventMeta.objects.create(event=event, **event_meta)
				response['repeat_pattern'] = EventMetaSerializer(meta).data
			return Response({"detail": {"code": "HTTP_201_OK", "message": "Событие создано"}, "data": response},
							status=201)
		response = {'detail': {
			"code": "BAD_REQUEST",
			"message": serializer.errors
		}}
		return Response(response, status=status.HTTP_400_BAD_REQUEST)

	@swagger_auto_schema(
		manual_parameters=[
			openapi.Parameter(
				'start_date',
				openapi.IN_QUERY,
				description='Начальная дата поиска в формате "2025-02-21"',
				type=openapi.TYPE_STRING,
				format=openapi.FORMAT_DATE,
				required=True
			),
			openapi.Parameter(
				'end_date',
				openapi.IN_QUERY,
				description='Конечная дата поиска в формате "2025-02-28"',
				type=openapi.TYPE_STRING,
				format=openapi.FORMAT_DATE,
				required=True
			),
			openapi.Parameter(
				'search',
				openapi.IN_QUERY,
				description='Поисковый запрос',
				type=openapi.TYPE_STRING
			)
		],
		responses={
			200: openapi.Response(description="Успешный ответ", schema=EventListSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"error": "string"}})
		},
		operation_summary="Получение всех событий пользователя",
		operation_description="Выводит список всех событий пользователя за определенный временной интервал.\n"
							  "Необходимо передать начальную и конечную дату, которые будут включены в интервал поиска.\n"
							  "События отсортированы по дате и времени начала.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'."
	)
	def list(self, request, *args, **kwargs):
		response = []
		user = request.user
		filter_start = request.GET.get('start_date')
		filter_end = request.GET.get('end_date')
		search = request.GET.get('search', '')

		if filter_start > filter_end:
			return Response(
				{"detail": {"code": "BAD_REQUEST", "message": "Некорректный временной диапазон"}},
				status=400)

		try:
			# получаем все события без повторений в переданном временном интервале
			events = Event.objects.filter(Q(users__pk=user.id) | Q(author=user), title__icontains=search, repeats=False,
										  start_date__lte=filter_end, end_date__gte=filter_start).distinct()
			# получаем все события с повторениями в интервале start_date - end_repeat
			repeated_events = Event.objects.filter(Q(users__pk=user.id) | Q(author=user), Q(end_repeat__gte=filter_start)
												   | Q(end_repeat__isnull=True), title__icontains=search, repeats=True,
												   start_date__lte=filter_end).distinct()
		except ValidationError:
			return Response(
				{"detail": {"code": "BAD_REQUEST", "message": "Некорректная дата"}},
				status=400)

		for repeated_event in repeated_events:
			duration = repeated_event.end_date - repeated_event.start_date
			# получаем метаданные, описывающие паттерн повторений события
			# если вдруг у повторяющегося события нет метаданных, пропускаем это событие, чтобы избежать ошибки
			try:
				metadata = EventMetaSerializer(repeated_event.eventmeta).data
			except:
				continue
			# передаем данные в функцию, которая вычисляет все повторения в заданном диапазоне времени,
			# и возвращает список объектов datetime
			event_dates = get_dates(metadata, filter_start, filter_end, repeated_event.start_date, repeated_event.end_date,
									repeated_event.end_repeat)
			print('dates: ', event_dates)

			# переводим date в datetime с помощью функции combine
			event_start_datetime = datetime.combine(repeated_event.start_date, time.min)
			# если дата начала события не соответствует паттерну повторений, но находится в диапазоне фильтрации,
			# добавляем ее в список дат
			if (repeated_event.start_date <= datetime.date(parse(filter_end))
					and repeated_event.end_date >= datetime.date(parse(filter_start))
					and event_start_datetime not in event_dates):
				event_dates.append(event_start_datetime)

			# получаем даты отмененных событий в заданном временном интервале и удаляем их из списка
			canceled_events = CanceledEvent.objects.filter(event=repeated_event, cancel_date__lte=filter_end,
														   cancel_date__gte=parse(filter_start)-duration)
			print('canceled_events: ', canceled_events)
			for canceled_event in canceled_events:
				# переводим date в datetime с помощью функции combine
				cancel_date = datetime.combine(canceled_event.cancel_date, time.min)
				if cancel_date in event_dates:
					event_dates.remove(cancel_date)

			for event_date in event_dates:
				repeated_event.start_date = datetime.date(event_date)
				repeated_event.end_date = datetime.date(event_date) + duration
				response.append(EventListSerializer(repeated_event, context={'request': request}).data)

		for event in events:
			response.append(EventListSerializer(event, context={'request': request}).data)
		# сортируем итоговый список событий сперва по дате, а затем по времени
		response.sort(key=lambda x: (x['start_date'], x['start_time'] if x['start_time'] is not None else ''))
		return Response({"detail": {"code": "HTTP_200_OK", "message": "Получен список событий пользователя"},
						 "data": response}, status=200)

	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный ответ", schema=EventResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация",
								  examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Событие не найдено", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса",
								  examples={"application/json": {"error": "string"}})
		},
		operation_summary="Получение события по id",
		operation_description="Получает данные события по его id.\nУсловия доступа к эндпоинту: токен авторизации в "
							  "формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'")
	def retrieve(self, request, pk):
		cache_key = f"event_{pk}"
		event = cache.get(cache_key)
		print('event: ', event)
		print('cache_keys: ', cache.keys('*'))
		logger.info(f'Ключи в кэше: {cache.keys("*")}')
		if not event:
			logger.info(f'События с id = {pk} нет в кэше')
			print('1')
			event = self.get_object()
			cache.set(cache_key, event)
		response_data = {"event_data": EventSerializer(event, context={'request': request}).data}
		try:
			response_data["repeat_pattern"] = EventMetaSerializer(event.eventmeta).data
		except:
			pass
		response = {"detail": {"code": "HTTP_200_OK", "message": "Данные события получены."},
					"data": response_data}
		return Response(response, status=200)

	@swagger_auto_schema(
		manual_parameters=[
			openapi.Parameter(
				'cancel_date',
				openapi.IN_QUERY,
				description='Дата в формате "2025-02-28", передается только при удалении повторяющихся событий',
				type=openapi.TYPE_STRING,
				format=openapi.FORMAT_DATE,
				),
			openapi.Parameter(
				'all',
				openapi.IN_QUERY,
				description='Передавать all=true, если удаляются все повторения, false передавать необязательно',
				type=openapi.TYPE_BOOLEAN
			)
			],
		responses={
			204: openapi.Response(description="Успешное удаление события"),
			401: openapi.Response(description="Требуется авторизация",
								  examples={"application/json": {"detail": "string"}}),
			403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Событие не найдено", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса",
								  examples={"application/json": {"error": "string"}})
		},
		operation_summary="Удаление события по id",
		operation_description="Удаляет событие из базы данных по его id.\n"
							  "При удалении повторяющихся событий надо передать параметр cancel_date.\n"
							  "Если удаляются все повторы события в будущем, надо передать параметр all=true.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'\n"
							  "Пользователь может удалить только созданное им событие."
	)
	def destroy(self, request, pk):
		event = self.get_object()
		cancel_date = request.GET.get('cancel_date')
		all_param = request.GET.get('all')
		# удаляем неповторяющиеся события
		if not cancel_date:
			event.delete()
		# удаляем повторяющиеся события
		else:
			# чтобы удалить все повторы события, меняем дату окончания повторов на переданную
			if all_param == 'true':
				event.end_repeat = datetime.date(parse(cancel_date) - timedelta(days=1))
				event.save()
			# чтобы удалить только один повтор события, делаем запись в БД в таблицу CanceledEvent
			else:
				CanceledEvent.objects.create(event=event, cancel_date=cancel_date)
		return Response(status=204)

	@swagger_auto_schema(
		manual_parameters=[
			openapi.Parameter(
				'change_date',
				openapi.IN_QUERY,
				description='Дата в формате "2025-02-28", передается только при редактировании повторяющихся событий',
				type=openapi.TYPE_STRING,
				format=openapi.FORMAT_DATE,
			),
			openapi.Parameter(
				'all',
				openapi.IN_QUERY,
				description='Передавать all=true, если редактируются все повторения, false передавать необязательно',
				type=openapi.TYPE_BOOLEAN
			)
		],
		responses={
			200: openapi.Response(description="Успешный ответ", schema=EventResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация",
								  examples={"application/json": {"detail": "string"}}),
			403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Событие не найдено", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса",
								  examples={"application/json": {"error": "string"}})
		},
		operation_summary="Редактирование события по id",
		operation_description="Эндпоинт для редактирования события.\n"
							  "При редактировании повторяющихся событий надо передавать параметр change_date, соответствующий дате начала события.\n"
							  "Если редактируются все повторы события, то надо передать параметр all=true.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'\n"
							  "Пользователь может редактировать только созданное им событие."
	)
	def partial_update(self, request, pk):
		serializer = self.get_serializer(data=request.data)
		change_date = request.GET.get('change_date')
		all_param = request.GET.get('all')

		if serializer.is_valid():
			event = self.get_object()
			event_data = serializer.validated_data.get('event_data')
			event_meta = serializer.validated_data.get('repeat_pattern')

			# если надо отредактировать повторяющееся событие, то создаем его копию в БД и редактируем именно ее
			if change_date:
				old_users = event.users.all()
				event_duration = event.end_date - event.start_date
				# копируем исходное событие и создаем новый объект, меняя даты начала и конца события
				event.pk = None
				event.start_date = change_date
				event.end_date = datetime.date(parse(change_date)) + event_duration
				event.save()
				# добавляем прежних участников события
				event.users.set(old_users)

				# достаем исходное событие
				old_event = Event.objects.get(id=pk)
				# если редактируем все повторы события, то меняем дату окончания повторов исходного события на
				# предшествующую change_date, то есть удаляем все повторы в будущем
				if all_param == 'true':
					if not event_data or 'repeats' not in event_data or event_data['repeats'] is True:
						# добавляем старые метаданные к новому событию, если пользователь при редактировании не убрал повторы
						old_meta = old_event.eventmeta
						old_meta.pk = None
						old_meta.event = event
						old_meta.save()
					# меняем дату окончания повторов исходного события
					old_event.end_repeat = datetime.date(parse(change_date) - timedelta(days=1))
					old_event.save()
				# если надо отредактировать только одно повторяющееся событие, то удаляем его из повторяющихся и ставим
				# отдельной записью в таблицу, как неповторяющееся
				else:
					event.repeats = False
					event.end_repeat = None
					event.save()
					# добавляем событие в таблицу отмененных
					CanceledEvent.objects.create(event=old_event, cancel_date=change_date)

			# если переданы данные события, то обновляем их
			if event_data:
				new_users = event_data.pop('users', None)
				Event.objects.filter(id=event.id).update(**event_data)
				# если передан список участников события, обновляем его в БД
				if new_users:
					old_users = event.users.all()
					for user in old_users:
						if user not in new_users:
							event.users.remove(user)
					for user in new_users:
						if user not in old_users:
							event.users.add(user)
				event = Event.objects.get(id=event.id)

			# если переданы метаданные события, то обновляем их
			if event_meta:
				EventMeta.objects.update_or_create(event=event, defaults=event_meta)

			response_data = {"event_data": EventSerializer(event, context={'request': request}).data}
			try:
				response_data["repeat_pattern"] = EventMetaSerializer(event.eventmeta).data
			except:
				pass
			return Response(
				{"detail": {"code": "HTTP_200_OK", "message": "Событие успешно изменено"},
				 "data": response_data}, status=200)

		response = {'detail': {
			"code": "BAD_REQUEST",
			"message": serializer.errors
		}}
		return Response(response, status=status.HTTP_400_BAD_REQUEST)


