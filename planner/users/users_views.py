from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins, status
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.decorators import action
from .users_serializers import (YandexAuthSerializer, UserLoginSerializer, LoginResponseSerializer,
								ErrorResponseSerializer, VKAuthSerializer, MailAuthSerializer, SignupSerializer,
								ResetPasswordSerializer, UserResponseSerializer, UserUpdateSerializer, CodeSerializer)
from .services import get_user_from_yandex, get_user_from_vk, get_user, create_user, send_password
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import UserProfile, Group, SignupCode, GroupUser
from django.http import HttpResponse
from drf_yasg import openapi
from planner.permissions import UserPermission, GroupPermission
from datetime import timedelta
from django.utils import timezone
import logging
from django.core.cache import cache


logger = logging.getLogger('users')


class UserViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
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
		elif self.action == 'partial_update':
			return UserUpdateSerializer
		else:
			return UserLoginSerializer

	@swagger_auto_schema(
		responses={
			204: openapi.Response(description="Успешное удаление пользователя"),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Пользователь не найден", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
																									{"error": "string"}})
		},
		operation_summary="Удаление пользователей по id",
		operation_description="Удаляет учетную запись пользователя из базы данных по его id.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате "
							  "'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'\n"
							  "Пользователь может удалить только свой собственный профиль.")
	def destroy(self, request, pk):
		user = self.get_object()
		user.delete()
		# удаляем данные пользователя из кэша, если они там есть
		try:
			cache_key = f"user_{pk}"
			logger.info(f'User data in cache before removal: {cache.get(cache_key)}')
			if cache_key in cache.keys("*"):
				cache.delete(cache_key)
				logger.info(f'User data in cache after removal: {cache.get(cache_key)}')
		except:
			logger.info('Something went wrong with cache processing.')

		return Response(status=204)

	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный ответ", schema=UserResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Пользователь не найден", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
																									{"error": "string"}})
		},
		operation_summary="Получение данных пользователя по id",
		operation_description="Получает данные профиля пользователя по его id.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате "
							  "'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'\n"
							  "Пользователь может просматривать только свой собственный профиль.")
	def retrieve(self, request, pk):
		try:
			# пробуем получить данные пользователя из кэша
			# берем id из данных авторизованного пользователя, а не url, чтобы обеспечить санкционированный допуск к кэшу
			cache_key = f"user_{request.user.id}"
			user_data = cache.get(cache_key)
			if user_data:
				logger.info(f'User "{user_data}" was received from cache')
			else:
				# если данных пользователя нет в кэше, добавляем их туда
				logger.info(f'User with id = {request.user.id} is absent in cache')
				user = self.get_object()
				user_data = self.get_serializer(user).data
				cache.set(cache_key, user_data)
		except:
			logger.info('Something went wrong with cache processing.')
			user = self.get_object()
			user_data = self.get_serializer(user).data

		response = {"detail": {"code": "HTTP_200_OK", "message": "Данные пользователя получены."}, "data": user_data}
		return Response(response, status=200)

	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешное редактирование профиля", schema=UserResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Пользователь не найден", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
																									{"error": "string"}})
		},
		operation_summary="Редактирование данных пользователя по id",
		operation_description="Редактирует данные профиля пользователя по его id.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате "
							  "'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'\n"
							  "Пользователь может реактировать только свой собственный профиль.")
	def partial_update(self, request, pk):
		user = self.get_object()
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			user.first_name = serializer.validated_data.get('first_name', user.first_name)
			user.save()
			user_data = UserLoginSerializer(user).data

			# обновляем данные пользователя в кэше
			cache_key = f"user_{pk}"
			try:
				logger.info(f'Data in cache before update: {cache.get(cache_key)}')
				cache.set(cache_key, user_data)
				logger.info(f'Data in cache after update: {cache.get(cache_key)}')
			except:
				logger.info('Something went wrong with cache processing.')

			return Response({"detail": {"code": "HTTP_200_OK", "message": "Данные пользователя отредактированы."},
																			"data": user_data}, status=200)

		response = {'detail': {
			"code": "BAD_REQUEST",
			"message": serializer.errors
		}}
		return Response(response, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=False, methods=['post'])
	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешная авторизация", schema=LoginResponseSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			401: openapi.Response(description="Требуется подтвеждение авторизации по коду", examples={"application/json":
												  {"detail": {"code": "string", "message": "string"}, "data": "string"}}),
			403: openapi.Response(description="Доступ запрещен", schema=ErrorResponseSerializer()),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
																									{"error": "string"}})
		},
		operation_summary="Авторизация пользователей по email",
		operation_description="Авторизация пользователей по email и пароль.\n"
							  "Если пользователь ранее регистрировался через соцсети, ему на почту высылается код "
							  "подтверждения, а в поле 'data' возвращается его id. Полученный id следует передать в "
							  "эндпоинте api/users/verify_code для верификации введенного пользователем кода.\n"
							  "После успешной верификации в БД записывается введенный пароль и разрешается вход в приложение."
	)
	def mail_auth(self, request):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			response_data = get_user(**serializer.validated_data)
			logger.info(f"Attempt to sign in by email {serializer.validated_data['email']}. Result -"
						f"{response_data[0]}")
			return Response(response_data[0], status=response_data[1])

		response = {'detail': {
			"code": "BAD_REQUEST",
			"message": serializer.errors
		}}
		return Response(response, status=status.HTTP_400_BAD_REQUEST)

	@swagger_auto_schema(
		responses={
			201: openapi.Response(description="Успешная регистрация", examples={"application/json": {"detail":
														 {"code": "string", "message": "string"}, "data": "string"}}),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			403: openapi.Response(description="Доступ запрещен", schema=ErrorResponseSerializer()),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
																									{"error": "string"}})
		},
		operation_summary="Регистрация пользователей по email",
		operation_description="Регистрация пользователей по email и пароль.\n"
							  "Создает нового пользователя в базе данных с неактивным статусом.\n"
							  "Принимает email и пароль пользователя и при успешной регистрации возвращает его id.\n"
							  "Полученный id следует передать в эндпоинте api/users/verify_code для верификации введенного "
							  "пользователем кода.\n"
							  "Регистрация разрешается, только если пользователя с таким email не существует в базе данных "
							  "или его профиль не был активирован."
	)
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			email = serializer.validated_data['email']
			password = serializer.validated_data['password']

			# проверяем, есть ли пользователь с таким email в БД
			user = User.objects.filter(email__iexact=email).first()
			# если найден пользователь с неактивным аккаунтом, то удаляем его
			if user and not user.is_active:
				user.delete()
			# если найден пользователь с активным аккаунтом, запрещаем регистрацию
			elif user and user.is_active:
				logger.info(f"Attempt to sign up by existing email {email}.")
				return Response({"detail": {"code": "HTTP_403_FORBIDDEN", "message": "Пользователь с таким email адресом "
																	 "уже зарегистрирован в приложении"}}, status=403)
			response_data = create_user(email, password)
			logger.info(f"A user was sign up by email {email}.")
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
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
																									{"error": "string"}})
		},
		operation_summary="Восстановление пароля пользователя",
		operation_description="Восстановление пароля пользователя по email.\n"
							  "Принимает email пользователя, и если такой email найден в БД, высылает на него новый "
							  "случайно сгенерированный пароль."
	)
	def reset_password(self, request):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			email = serializer.validated_data['email']
			response_data = send_password(email)
			logger.info(f"Attempt to reset password by email {email}. Result - {response_data[0]}")
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
				logger.info(f"User with email {response_data[0].get('user_data').get('email')} and "
							f"id = {response_data[0].get('user_data').get('id')} was authorized")
				response = {
					"detail": {"code": "HTTP_200_OK", "message": "Авторизация прошла успешно"},
					"data": response_data[0]
				}
				return Response(response, status=status.HTTP_200_OK)
			logger.info(f"Authorization with Yandex failed. Details: {response_data[0]}")
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
			code_verifier = serializer.validated_data['code_verifier'] if 'code_verifier' in serializer.validated_data \
				else None
			code = serializer.validated_data['code'] if 'code' in serializer.validated_data else None
			device_id = serializer.validated_data['device_id']
			state = serializer.validated_data['state']
			response_data = get_user_from_vk(code_verifier, code, device_id, state)
			if response_data[1] == 200:
				logger.info(f"User with email {response_data[0].get('user_data').get('email')} and "
							f"id = {response_data[0].get('user_data').get('id')} was authorized")
				response = {
					"detail": {"code": "HTTP_200_OK", "message": "Авторизация прошла успешно"},
					"data": response_data[0]
				}
				return Response(response, status=status.HTTP_200_OK)
			logger.info(f"Authorization with VK failed. Details: {response_data[0]}")
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
			404: openapi.Response(description="Пользователь не найден", examples={"application/json":
																					  {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
																									{"error": "string"}})
		},
		operation_summary="Подтверждение регистрации пользователя по коду",
		operation_description="Эндпоинт для подтверждения кода, высланного по email при регистрации.\n"
							  "Принимает id пользователя и код и при успешной проверке возвращает токен пользователя.\n"
							  "Код работает в течение 1 часа, после чего выдается ошибка 'код устарел'."
	)
	def verify_code(self, request, pk=None):
		user = self.get_object()
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			code = serializer.validated_data['code']
			# проверяем принадлежность кода пользователю
			if SignupCode.objects.filter(code=code, user=user).exists():
				signup_code = SignupCode.objects.get(code=code, user=user)
				# проверяем, что код действителен
				if timezone.now() - signup_code.code_time < timedelta(minutes=60):
					# активируем профиль пользователя
					user.is_active = True
					user.save()
					# удаляем использованный код из БД
					signup_code.delete()
					# создаем дефолтную группу и ее участника, если они отсутствуют
					group, created = Group.objects.get_or_create(owner=user, default=True,
															defaults={'name': 'default_group', 'color': 'default_color'})
					if created:
						GroupUser.objects.get_or_create(user=user, group=group, defaults={'user_name': 'me'})
					# генерируем или получаем токен авторизации для пользователя
					token, created = Token.objects.get_or_create(user=user)
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


# функция для добавления отсутствующих профилей пользователей на проде
def add_missing_profiles(request):
	users = User.objects.all()
	for user in users:
		created = UserProfile.objects.get_or_create(user=user)
		print(user.username, ' : ', created)
	print("all done")
	return HttpResponse("It's done.")





