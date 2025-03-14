from datetime import datetime

from django.core.exceptions import ValidationError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Event, EventMeta
from .serializers import EventSerializer, EventMetaSerializer, EventCreateSerializer, EventListSerializer
from users.serializers import ErrorResponseSerializer
from django.db.models import Q
from .services import get_dates
from django.contrib.auth.models import User


class EventViewSet(viewsets.ModelViewSet):
	""" Эндпоинты для работы с событиями """
	queryset = Event.objects.all()
	http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
	parser_classes = (JSONParser, MultiPartParser)
	permission_classes = [IsAuthenticated]

	def get_serializer_class(self):
		if self.action == 'create':
			return EventCreateSerializer
		else:
			return EventSerializer

	@swagger_auto_schema(
		responses={
			201: openapi.Response(description="Успешное создание события", schema=EventCreateSerializer()),
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
			}
			# если были получены метаданные, делаем запись в таблице
			if event_meta:
				meta = EventMeta.objects.create(event=event, **event_meta)
				response.update(EventMetaSerializer(meta).data)
			return Response({"detail": {"code": "HTTP_201_OK", "message": "Событие создано"}, "data": response}, status=201)
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
			events = Event.objects.filter(Q(users__pk=user.id) | Q(author=user), repeats=False, start_date__lte=filter_end, end_date__gte=filter_start).distinct()
			# получаем все события с повторениями в интервале start_date - end_repeat
			repeated_events = Event.objects.filter(Q(users__pk=user.id) | Q(author=user), Q(end_repeat__gte=filter_start) | Q(end_repeat__isnull=True), repeats=True, start_date__lte=filter_end).distinct()
			print('repeated_events: ', repeated_events)
			for repeated_event in repeated_events:
				duration = repeated_event.end_date - repeated_event.start_date
				metadata = EventMetaSerializer(repeated_event.eventmeta).data
				print('metadata: ', metadata)
				event_dates = get_dates(metadata, filter_start, filter_end, repeated_event.start_date, repeated_event.end_date, repeated_event.end_repeat)
				print('dates: ', event_dates)
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
		response.sort(key=lambda x: (x['start_date'], x['start_time']))
		return Response({"detail": {"code": "HTTP_200_OK", "message": "Получен список событий пользователя"}, "data": response}, status=200)

	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный ответ", schema=EventSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Событие не найдено", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"error": "string"}})
		},
		operation_summary="Получение события по id",
		operation_description="Получает данные события по его id.\nУсловия доступа к эндпоинту: токен авторизации в "
							  "формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'")
	def retrieve(self, request, pk):
		event = self.get_object()
		response = {"detail": {"code": "HTTP_200_OK", "message": "Данные события получены."}, "data": self.get_serializer(event).data}
		return Response(response, status=200)