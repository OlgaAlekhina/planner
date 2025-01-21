from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins, status
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.decorators import action
from .serializers import (YandexAuthSerializer, UserLoginSerializer, LoginResponseSerializer, DetailSerializer,
						  ErrorResponseSerializer, VKAuthSerializer)
from .services import get_user_from_yandex, get_user_from_vk
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import UserProfile
from django.http import JsonResponse, HttpResponse
from drf_yasg import openapi
from planner.permissions import UserPermission


# endpoints for users
class UserViewSet(viewsets.ModelViewSet):
	"""
	delete: Удаляет учетную запись пользователя из базы данных по его id.
            Условия доступа к эндпоинту: токен авторизации в формате 'Token 3fa85f64-5717-4562-b3fc-2c963f66afa6'
            Пользователь может удалить только свой собственный профиль.
	"""
	queryset = User.objects.all()
	http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
	parser_classes = (JSONParser, MultiPartParser)
	permission_classes = [UserPermission]

	def get_serializer_class(self):
		if self.action == 'yandex_auth':
			return YandexAuthSerializer
		elif self.action == 'vk_auth':
			return VKAuthSerializer
		else:
			return UserLoginSerializer

	@swagger_auto_schema(
		responses={
			204: openapi.Response(description="Успешное удаление"),
			404: openapi.Response(description="Оъект не найден", examples={"application/json": {"detail": "string"}}),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"detail": "string"}})
		},
		operation_summary="Удаление пользователя по id")
	def destroy(self, request, pk):
		user = self.get_object()
		user.delete()
		return Response(status=204)

	@action(detail=False, methods=['post'])
	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный ответ", schema=LoginResponseSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			401: openapi.Response(description="Ошибка авторизации в сервисе Яндекса", schema=ErrorResponseSerializer()),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", schema=ErrorResponseSerializer())
		},
		operation_summary="Авторизация пользователей через Яндекс")
	def yandex_auth(self, request):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			oauth_token = serializer.validated_data['oauth_token']
			response_data = get_user_from_yandex(oauth_token)
			if response_data[1] == 200:
				response = {
					"detail": {"code": "HTTP_200_OK", "message": "Авторизация прошла успешно"},
					"data": response_data[0]
				}
				return Response(response, status=status.HTTP_200_OK)
			return Response(response_data[0], status=response_data[1])
		response = {'detail': {
			"code": "BAD_REQUEST",
			"message": serializer.errors
		}}
		return Response(response, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=False, methods=['post'])
	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный ответ", schema=LoginResponseSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", schema=ErrorResponseSerializer())
		},
		operation_summary="Авторизация пользователей через VK")
	def vk_auth(self, request):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			code_verifier = serializer.validated_data['code_verifier'] if 'code_verifier' in serializer.validated_data else None
			code = serializer.validated_data['code'] if 'code' in serializer.validated_data else None
			device_id = serializer.validated_data['device_id']
			state = serializer.validated_data['state']
			response_data = get_user_from_vk(code_verifier, code, device_id, state)
			if response_data[1] == 200:
				response = {
					"detail": {"code": "HTTP_200_OK", "message": "Авторизация прошла успешно"},
					"data": response_data[0]
				}
				return Response(response, status=status.HTTP_200_OK)
			return Response(response_data[0], status=response_data[1])
		response = {'detail': {
			"code": "BAD_REQUEST",
			"message": serializer.errors
		}}
		return Response(response, status=status.HTTP_400_BAD_REQUEST)


# функция для добавления отсутствующих профилей пользователей
def add_missing_profiles(request):
	users = User.objects.all()
	for user in users:
		created = UserProfile.objects.get_or_create(user=user)
		print(user.username, ' : ', created)
	print("all done")
	return HttpResponse("It's done.")