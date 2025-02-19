from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Event
from .serializers import EventSerializer
from users.serializers import ErrorResponseSerializer


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
			201: openapi.Response(description="Успешное создание группы", schema=EventSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"error": "string"}})
		},
		operation_summary="Создание нового события",
		operation_description="Создает новое событие для данного пользователя.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.\n"
	)
	def create(self, request):
		return Response('test')
		# serializer = self.get_serializer(data=request.data)
		# if serializer.is_valid():
		# 	name = serializer.validated_data['name']
		# 	user = request.user
		# 	group = Group.objects.create(owner=user, name=name)
		# 	GroupUser.objects.create(user=user, group=group, user_name=user.userprofile.nickname)
		# 	return Response({"detail": {"code": "HTTP_201_OK", "message": "Группа создана"}, "data": GroupSerializer(group).data}, status=201)
		# response = {'detail': {
		# 	"code": "BAD_REQUEST",
		# 	"message": serializer.errors
		# }}
		# return Response(response, status=status.HTTP_400_BAD_REQUEST)

	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный ответ", schema=EventSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"error": "string"}})
		},
		operation_summary="Получение всех событий пользователя",
		operation_description="Выводит список всех событий пользователя.\nУсловия доступа к эндпоинту: токен авторизации в "
							  "формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'"
	)
	def list(self, request):
		user = request.user
		print(Event.objects.filter(users__pk=user.id))
		# event_users = user.event_users.all()
		# events = []
		# for event_user in event_users:
		# 	events.append(event_user.event)
		# print('events: ', events)
		# response = []
		# for group_user in group_users:
		# 	response.append(GroupSerializer(group_user.group).data)
		# return Response({"detail": {"code": "HTTP_200_OK", "message": "Получен список групп пользователя"},
		# 				 "data": response}, status=200)
		return Response('test')
