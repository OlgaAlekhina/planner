import random
import string

from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins, status
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.decorators import action
from .serializers import (YandexAuthSerializer, UserLoginSerializer, LoginResponseSerializer, DetailSerializer,
						  ErrorResponseSerializer, VKAuthSerializer, MailAuthSerializer, GroupSerializer,
						  CodeSerializer, GroupUserSerializer, SignupSerializer, ResetPasswordSerializer,
						  GroupResponseSerializer, GroupUserResponseSerializer, GroupUsersResponseSerializer,
						  GroupListResponseSerializer)
from .services import get_user_from_yandex, get_user_from_vk, get_user, create_user, send_password
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import UserProfile, Group, SignupCode, GroupUser
from django.http import JsonResponse, HttpResponse
from drf_yasg import openapi
from planner.permissions import UserPermission, GroupPermission
from datetime import timedelta
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.ModelViewSet):
	""" Эндпоинты для работы с пользователями """
	queryset = User.objects.all()
	http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
	parser_classes = (JSONParser, MultiPartParser)
	permission_classes = [UserPermission]

	def get_serializer_class(self):
		if self.action == 'yandex_auth':
			return YandexAuthSerializer
		elif self.action == 'vk_auth':
			return VKAuthSerializer
		elif self.action == 'mail_auth':
			return MailAuthSerializer
		elif self.action == 'verify_code':
			return CodeSerializer
		elif self.action == 'create':
			return SignupSerializer
		elif self.action == 'reset_password':
			return ResetPasswordSerializer
		else:
			return UserLoginSerializer

	@swagger_auto_schema(
		responses={
			204: openapi.Response(description="Успешное удаление пользователя"),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Пользователь не найден", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"error": "string"}})
		},
		operation_summary="Удаление пользователей по id",
		operation_description="Удаляет учетную запись пользователя из базы данных по его id.\nУсловия доступа к эндпоинту: токен авторизации в "
							  "формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'\nПользователь может удалить только свой собственный профиль.")
	def destroy(self, request, pk):
		user = self.get_object()
		user.delete()
		return Response(status=204)

	@action(detail=False, methods=['post'])
	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешная авторизация", schema=LoginResponseSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			401: openapi.Response(description="Требуется подтвеждение авторизации по коду", examples={"application/json": {"detail": {"code": "string", "message": "string"}, "data": "string"}}),
			403: openapi.Response(description="Доступ запрещен", schema=ErrorResponseSerializer()),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"error": "string"}})
		},
		operation_summary="Авторизация пользователей по email",
		operation_description="Авторизация пользователей по email и пароль.\n"
							  "Если пользователь ранее регистрировался через соцсети, ему на почту высылается код подтверждения, а в поле 'data' возвращается его id."
							  "Полученный id следует передать в эндпоинте api/users/verify_code для верификации введенного пользователем кода.\n"
							  "После успешной верификации в БД записывается введенный пароль и разрешается вход в приложение."
	)
	def mail_auth(self, request):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			email = serializer.validated_data['email']
			password = serializer.validated_data['password']
			response_data = get_user(email, password)
			return Response(response_data[0], status=response_data[1])
		response = {'detail': {
			"code": "BAD_REQUEST",
			"message": serializer.errors
		}}
		return Response(response, status=status.HTTP_400_BAD_REQUEST)

	@swagger_auto_schema(
		responses={
			201: openapi.Response(description="Успешная регистрация", examples={"application/json": {"detail": {"code": "string", "message": "string"}, "data": "string"}}),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			403: openapi.Response(description="Доступ запрещен", schema=ErrorResponseSerializer()),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"error": "string"}})
		},
		operation_summary="Регистрация пользователей по email",
		operation_description="Регистрация пользователей по email и пароль.\n"
							  "Создает нового пользователя в базе данных с неактивным статусом.\n"
							  "Принимает email и пароль пользователя и при успешной регистрации возвращает его id.\n"
							  "Полученный id следует передать в эндпоинте api/users/verify_code для верификации введенного пользователем кода.\n"
							  "Регистрация разрешается, только если пользователя с таким email не существует в базе данных или его профиль не был активирован."
	)
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			email = serializer.validated_data['email']
			password = serializer.validated_data['password']
			# проверяем, есть ли пользователь с таким email в БД
			user = User.objects.filter(email=email).first()
			# если найден пользователь с неактивным аккаунтом, то удаляем его
			if user and not user.is_active:
				user.delete()
			# если найден пользователь с активным аккаунтом, запрещаем регистрацию
			if user and user.is_active:
				return Response({"detail": {"code": "HTTP_403_FORBIDDEN", "message": "Пользователь с таким email адресом уже зарегистрирован в приложении"}}, status=403)
			response_data = create_user(email, password)
			return Response(response_data[0], status=response_data[1])
		response = {'detail': {
			"code": "BAD_REQUEST",
			"message": serializer.errors
		}}
		return Response(response, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=False, methods=['post'])
	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный запрос", schema=ErrorResponseSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			403: openapi.Response(description="Доступ запрещен", schema=ErrorResponseSerializer()),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"error": "string"}})
		},
		operation_summary="Восстановление пароля пользователя",
		operation_description="Восстановление пароля пользователя по email.\n"
							  "Принимает email пользователя, и если такой email найден в БД, высылает на него новый случайно сгенерированный пароль."
	)
	def reset_password(self, request):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			email = serializer.validated_data['email']
			response_data = send_password(email)
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

	@action(detail=True, methods=['post'])
	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешное подтверждение регистрации", schema=LoginResponseSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			403: openapi.Response(description="Доступ запрещен", schema=ErrorResponseSerializer()),
			404: openapi.Response(description="Пользователь не найден", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"error": "string"}})
		},
		operation_summary="Подтверждение регистрации пользователя по коду",
		operation_description="Эндпоинт для подтверждения кода, высланного по email при регистрации.\n"
							  "Принимает id пользователя и код и при успешной проверке возвращает токен пользователя.\n"
							  "Код работает в течение 1 часа, после чего выдается ошибка 'код устарел'."
	)
	def verify_code(self, request, pk=None):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			code = serializer.validated_data['code']
			user = self.get_object()
			if SignupCode.objects.filter(code=code, user=user).exists():
				signup_code = SignupCode.objects.get(code=code, user=user)
				if timezone.now() - signup_code.code_time < timedelta(minutes=60):
					user.is_active = True
					user.save()
					signup_code.delete()
					token = Token.objects.get(user=user)
					user_data = UserLoginSerializer(user).data
					response = {
						"detail": {"code": "HTTP_200_OK", "message": "Код успешно подтвержден"},
						"data": {"user_data": user_data, "user_auth_token": token.key}
					}
					return Response(response, status=status.HTTP_200_OK)
				else:
					response = {
						"code": "HTTP_403_FORBIDDEN",
						"message": "Код устарел",
					}
					return Response(response, status=status.HTTP_400_BAD_REQUEST)
			else:
				response = {
					"code": "HTTP_403_FORBIDDEN",
					"message": "Код введен неверно",
				}
				return Response(response, status=status.HTTP_400_BAD_REQUEST)
		response = {
			"code": "BAD_REQUEST",
			"message": serializer.errors
		}
		return Response(response, status=status.HTTP_400_BAD_REQUEST)


class GroupViewSet(viewsets.ModelViewSet):
	""" Эндпоинты для работы с группами """
	queryset = Group.objects.all()
	http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
	parser_classes = (JSONParser, MultiPartParser)
	permission_classes = [IsAuthenticated, GroupPermission]

	def get_serializer_class(self):
		if self.action == 'add_user':
			return GroupUserSerializer
		# elif self.action == 'vk_auth':
		# 	return VKAuthSerializer
		# elif self.action == 'mail_auth':
		# 	return MailAuthSerializer
		else:
			return GroupSerializer

	@swagger_auto_schema(
		responses={
			201: openapi.Response(description="Успешное создание группы", schema=GroupResponseSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"error": "string"}})
		},
		operation_summary="Создание новой группы",
		operation_description="Создает новую группу для данного пользователя.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.\n"
	)
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			name = serializer.validated_data['name']
			user = request.user
			group = Group.objects.create(owner=user, name=name)
			GroupUser.objects.create(user=user, group=group, user_name=user.userprofile.nickname)
			return Response({"detail": {"code": "HTTP_201_OK", "message": "Группа создана"}, "data": GroupSerializer(group).data}, status=201)
		response = {'detail': {
			"code": "BAD_REQUEST",
			"message": serializer.errors
		}}
		return Response(response, status=status.HTTP_400_BAD_REQUEST)

	@swagger_auto_schema(
		responses={
			204: openapi.Response(description="Успешное удаление группы"),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Группа не найдена", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"error": "string"}})
		},
		operation_summary="Удаление группы по id",
		operation_description="Удаляет группу из базы данных по ее id и всех добавленных в нее пользователей с неактивными профилями.\nУсловия доступа к эндпоинту: токен авторизации в "
							  "формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'\nПользователь может удалить только созданную им группу."
	)
	def destroy(self, request, pk):
		group = self.get_object()
		# получаем список участников группы
		group_users = group.group_users.all()
		# для каждого участника группы получаем его профиль, и если он не был активирован, то удаляем его из БД
		for group_user in group_users:
			user = group_user.user
			if not user.is_active:
				user.delete()
		# удаляем группу
		group.delete()
		return Response(status=204)

	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный ответ"),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Группа не найдена", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"error": "string"}})
		},
		operation_summary="Редактирование группы по id",
		operation_description="Эндпоинт для редактирования названия группы.\nУсловия доступа к эндпоинту: токен авторизации в "
							  "формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'\nПользователь может редактировать только созданную им группу."
	)
	def partial_update(self, request, pk):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			name = serializer.validated_data['name']
			group = self.get_object()
			group.name = name
			group.save()
			return Response(
				{"detail": {"code": "HTTP_200_OK", "message": "Группа успешно изменена"}, "data": GroupSerializer(group).data}, status=200)
		response = {'detail': {
			"code": "BAD_REQUEST",
			"message": serializer.errors
		}}
		return Response(response, status=status.HTTP_400_BAD_REQUEST)

	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный ответ", schema=GroupListResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"error": "string"}})
		},
		operation_summary="Получение всех групп пользователя",
		operation_description="Выводит список всех групп пользователя.\nУсловия доступа к эндпоинту: токен авторизации в "
							  "формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'"
	)
	def list(self, request):
		user = request.user
		group_users = user.users.all()
		response = []
		for group_user in group_users:
			response.append(GroupSerializer(group_user.group).data)
		return Response({"detail": {"code": "HTTP_200_OK", "message": "Получен список групп пользователя"},
						 "data": response}, status=200)

	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный ответ", schema=GroupUsersResponseSerializer),
			401: openapi.Response(description="Требуется авторизация",
								  examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Группа не найдена", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса",
								  examples={"application/json": {"error": "string"}})
		},
		operation_summary="Получение всех участников группы",
		operation_description="Выводит всех участников группы.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.\n"
	)
	def retrieve(self, request, pk):
		group = self.get_object()
		group_users = group.group_users.all()
		response = []
		for group_user in group_users:
			response.append(GroupUserSerializer(group_user).data)
		return Response({"detail": {"code": "HTTP_200_OK", "message": "Получен список участников группы"},
						 "data": response}, status=200)

	@action(detail=True, methods=['post'])
	@swagger_auto_schema(
		responses={
			201: openapi.Response(description="Успешное добавление участника", schema=GroupUserResponseSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Группа не найдена", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json": {"error": "string"}})
		},
		operation_summary="Добавление участника в группу",
		operation_description="Добавляет нового участника в группу.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.\n"
							  "Добавить участника может только владелец группы."
	)
	def add_user(self, request, pk):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			user_name = serializer.validated_data['user_name']
			user_role = serializer.validated_data['user_role']
			user_color = serializer.validated_data['user_color']
			group = self.get_object()
			# генерируем уникальное имя для создания нового пользователя и проверяем, что такого имени нет в БД
			for _ in range(10):
				username = f"{user_name}-{''.join(random.choices(string.ascii_letters + string.digits, k=8))}"
				if not User.objects.filter(username=username):
					break
			# сначала создаем нового пользователя
			user = User.objects.create_user(username=username)
			user.is_active = False
			user.save()
			# затем добавляем его в группу
			group_user = GroupUser.objects.create(user=user, group=group, user_name=user_name, user_role=user_role, user_color=user_color)
			return Response({"detail": {"code": "HTTP_201_OK", "message": "Участник добавлен в группу"}, "data": GroupUserSerializer(group_user).data}, status=201)
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