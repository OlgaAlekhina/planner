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


# endpoints for users
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
	parser_classes = (JSONParser, MultiPartParser)

	def get_serializer_class(self):
		if self.action == 'yandex_auth':
			return YandexAuthSerializer
		elif self.action == 'vk_auth':
			return VKAuthSerializer
		else:
			return UserLoginSerializer

	@action(detail=False, methods=['post'])
	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный ответ", schema=LoginResponseSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных", examples={"application/json": {"field_name": ["error_messages"]}}),
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
				response_data = response_data[0]
				user_id = response_data.get('id')
				user = User.objects.get(id=user_id)
				token = Token.objects.get(user=user)
				response = {
					"detail": {"code": "HTTP_200_OK", "message": "Авторизация прошла успешно"},
					"data": {"user_data": response_data, "user_auth_token": token.key}
				}
				return Response(response, status=status.HTTP_200_OK)
			return Response(response_data[0], status=response_data[1])

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=False, methods=['post'])
	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный ответ", schema=LoginResponseSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных",
								  examples={"application/json": {"field_name": ["error_messages"]}}),
			401: openapi.Response(description="Ошибка авторизации в сервисе Яндекса", schema=ErrorResponseSerializer()),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", schema=ErrorResponseSerializer())
		},
		operation_summary="Авторизация пользователей через VK ID")
	def vk_auth(self, request):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			code_verifier = serializer.validated_data['code_verifier']
			code = serializer.validated_data['code']
			device_id = serializer.validated_data['device_id']
			state = serializer.validated_data['state']
			response_data = get_user_from_vk(code_verifier, code, device_id, state)
			if response_data[1] == 200:
				response_data = response_data[0]
				user_id = response_data.get('id')
				user = User.objects.get(id=user_id)
				token = Token.objects.get(user=user)
				response = {
					"detail": {"code": "HTTP_200_OK", "message": "Авторизация прошла успешно"},
					"data": {"user_data": response_data, "user_auth_token": token.key}
				}
				return Response(response, status=status.HTTP_200_OK)
			return Response(response_data[0], status=response_data[1])

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# функция для добавления отсутствующих профилей пользователей
def add_missing_profiles(request):
	users = User.objects.all()
	for user in users:
		created = UserProfile.objects.get_or_create(user=user)
		print(user.username, ' : ', created)
	print("all done")
	return HttpResponse("It's done.")