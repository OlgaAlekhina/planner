from datetime import datetime, time, date
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
from django.contrib.auth.models import User
from planner.permissions import EventPermission


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
	)
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			user = request.user
			event_data = serializer.validated_data.get('event_data')
			event_meta = serializer.validated_data.get('repeat_pattern')
			users = event_data.pop('users')
			# создаем новое событие в БД
			event = Event.objects.create(author=user, **event_data)
			# добавляем участников события вручную
			for user in users:
				event.users.add(user)
			response = {
				'event_data': EventSerializer(event).data,
				'repeat_pattern': {}
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
				description='Начальная дата в формате "2025-02-21"',
				type=openapi.TYPE_STRING,
				format=openapi.FORMAT_DATE,
				required=True
			),
			openapi.Parameter(
				'end_date',
				openapi.IN_QUERY,
				description='Конечная дата в формате "2025-02-28"',
				type=openapi.TYPE_STRING,
				format=openapi.FORMAT_DATE,
				required=True
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
							  "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'"
	)
	def list(self, request, *args, **kwargs):
		response = []
		user = request.user
		filter_start = request.GET.get('start_date')
		filter_end = request.GET.get('end_date')
		if filter_start > filter_end:
			return Response(
				{"detail": {"code": "BAD_REQUEST", "message": "Некорректный временной диапазон"}},
				status=400)
		try:
			# получаем все события без повторений в нужном временном интервале
			events = Event.objects.filter(Q(users__pk=user.id) | Q(author=user), repeats=False, start_date__lte=filter_end,
										  end_date__gte=filter_start).distinct()
			# получаем все события с повторениями в интервале start_date - end_repeat
			repeated_events = Event.objects.filter(Q(users__pk=user.id) | Q(author=user), Q(end_repeat__gte=filter_start)
												   | Q(end_repeat__isnull=True), repeats=True, start_date__lte=filter_end).distinct()
			print('repeated_events: ', repeated_events)
			for repeated_event in repeated_events:
				duration = repeated_event.end_date - repeated_event.start_date
				# получаем метаданные, описывающие паттерн повторений события
				metadata = EventMetaSerializer(repeated_event.eventmeta).data
				# передаем данные в функцию, которая вычисляет все повторения в заданном диапазоне времени,
				# и возвращает список объектов datetime
				event_dates = get_dates(metadata, filter_start, filter_end, repeated_event.start_date, repeated_event.end_date,
										repeated_event.end_repeat)
				print('dates: ', event_dates)
				event_start_datetime = datetime.combine(repeated_event.start_date, time.min)
				# если дата начала события не соответствует паттерну повторений, но находится в диапазоне фильтрации,
				# добавляем ее в список дат
				if (repeated_event.start_date <= datetime.date(parse(filter_end)) and repeated_event.end_date >= datetime.date(parse(filter_start))
															  and event_start_datetime not in event_dates):
					event_dates.append(event_start_datetime)
					print('dates2: ', event_dates)
				# получаем даты отмененных событий в заданном временном интервале
				canceled_events = CanceledEvent.objects.filter(event=repeated_event, cancel_date__lte=filter_end,
															   cancel_date__gte=parse(filter_start)-duration)
				print('canceled_events: ', canceled_events)
				for event_date in event_dates:
					repeated_event.start_date = datetime.date(event_date)
					repeated_event.end_date = datetime.date(event_date) + duration
					response.append(EventListSerializer(repeated_event).data)
		except ValidationError:
			return Response(
				{"detail": {"code": "BAD_REQUEST", "message": "Некорректная дата"}},
				status=400)
		for event in events:
			response.append(EventListSerializer(event).data)
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
		event = self.get_object()
		response_data = {"event_data": self.get_serializer(event).data, "repeat_pattern": {}}
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
				description='Дата в формате "2025-02-28", передается только в том случае, когда надо удалить '
							'повторяющееся событие только в конкретный день',
				type=openapi.TYPE_STRING,
				format=openapi.FORMAT_DATE,
				),
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
							  "Чтобы удалить только одно повторяющееся событие на конкретную дату, надо передать параметр cancel_date.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'\n"
							  "Пользователь может удалить только созданное им событие."
	)
	def destroy(self, request, pk):
		event = self.get_object()
		cancel_date = request.GET.get('cancel_date')
		# если надо удалить событие вместе с повторами из БД
		if not cancel_date:
			event.delete()
		# чтобы удалить только один повтор события, делаем запись в БД в таблицу CanceledEvent
		else:
			CanceledEvent.objects.create(event=event, cancel_date=cancel_date)
		return Response(status=204)

	@swagger_auto_schema(
		manual_parameters=[
			openapi.Parameter(
				'change_date',
				openapi.IN_QUERY,
				description='Дата в формате "2025-02-28", передается только в том случае, когда надо отредактировать '
							'повторяющееся событие только в конкретный день',
				type=openapi.TYPE_STRING,
				format=openapi.FORMAT_DATE,
			),
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
							  "Чтобы редактировать только одно повторяющееся событие на конкретную дату, надо передать параметр change_date.\n"
							  "Если пользователь удаляет повторения события в будущем, то надо установить поле end_repeat = start_date.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'\n"
							  "Пользователь может редактировать только созданное им событие."
	)
	def partial_update(self, request, pk):
		serializer = self.get_serializer(data=request.data)
		change_date = request.GET.get('change_date')

		if serializer.is_valid():
			event = self.get_object()
			event_data = serializer.validated_data.get('event_data')
			event_meta = serializer.validated_data.get('repeat_pattern')

			# если надо отредактировать только одно повторяющееся событие, удаляем его из повторяющихся и ставим отдельной
			# записью в таблицу, как неповторяющееся
			if change_date:
				old_users = event.users.all()
				event_duration = event.end_date - event.start_date
				# добавляем событие в таблицу отмененных
				CanceledEvent.objects.create(event=event, cancel_date=change_date)
				# копируем исходное событие и создаем новый объект, меняя некоторые атрибуты
				event.pk = None
				event.start_date = change_date
				event.end_date = parse(change_date) + event_duration
				event.repeats = False
				event.end_repeat = None
				event.save()
				# добавляем участников события
				event.users.set(old_users)

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

			response_data = {"event_data": EventSerializer(event).data, "repeat_pattern": {}}
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


