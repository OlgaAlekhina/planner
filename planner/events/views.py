from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Event
from .serializers import EventSerializer
from users.serializers import ErrorResponseSerializer
from django.contrib.auth.models import User


class EventViewSet(viewsets.ModelViewSet):
	""" Эндпоинты для работы с событиями """
	queryset = Event.objects.all()
	http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
	parser_classes = (JSONParser, MultiPartParser)
	permission_classes = [IsAuthenticated]

	def get_serializer_class(self):
		if self.action == 'add_user':
			return EventSerializer
		else:
			return EventSerializer

	@swagger_auto_schema(
		responses={
			201: openapi.Response(description="Успешное создание события", schema=EventSerializer()),
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
			title = serializer.validated_data['title']
			location = serializer.validated_data['location'] if 'location' in serializer.validated_data else None
			start_date = serializer.validated_data['start_date']
			end_date = serializer.validated_data['end_date']
			start_time = serializer.validated_data['start_time'] if 'start_time' in serializer.validated_data else None
			end_time = serializer.validated_data['end_time'] if 'end_time' in serializer.validated_data else None
			users = serializer.validated_data['users']
			event = Event.objects.create(
				title=title, location=location, start_date=start_date, end_date=end_date, start_time=start_time, end_time=end_time
			)
			for user in users:
				event.users.add(user)
			return Response({"detail": {"code": "HTTP_201_OK", "message": "Событие создано"}, "data": EventSerializer(event).data}, status=201)
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
			200: openapi.Response(description="Успешный ответ", schema=EventSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"error": "string"}})
		},
		operation_summary="Получение всех событий пользователя",
		operation_description="Выводит список всех событий пользователя за определенный временной интервал.\n"
							  "Необходимо передать начальную и конечную дату, которые будут включены в интервал поиска.\n"
							  "События отсортированы по времени начала.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'"
	)
	def list(self, request, *args, **kwargs):
		user = request.user
		start_date = request.GET.get('start_date')
		end_date = request.GET.get('end_date')
		events = Event.objects.filter(users__pk=user.id, start_date__range=[start_date, end_date]).order_by('start_time')
		response = []
		for event in events:
			response.append(EventSerializer(event).data)
		return Response({"detail": {"code": "HTTP_200_OK", "message": "Получен список событий пользователя"}, "data": response}, status=200)

