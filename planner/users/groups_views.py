import random
import string
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.decorators import action
from .users_serializers import ErrorResponseSerializer
from .groups_serializers import (GroupSerializer, GroupUserSerializer, GroupResponseSerializer,
                                 GroupUserResponseSerializer, GroupUsersResponseSerializer, GroupListResponseSerializer,
                                 InvitationSerializer, GroupUserListResponseSerializer)
from rest_framework.response import Response
from .models import Group, GroupUser
from django.http import HttpResponse
from drf_yasg import openapi
from planner.permissions import UserPermission, GroupPermission
from datetime import date
from rest_framework.permissions import IsAuthenticated
import logging


logger = logging.getLogger('users')


class GroupViewSet(viewsets.ModelViewSet):
	""" Эндпоинты для работы с группами """
	queryset = Group.objects.all()
	http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
	parser_classes = (JSONParser, MultiPartParser)
	permission_classes = [IsAuthenticated, GroupPermission]

	def get_serializer_class(self):
		if self.action in ('add_user', 'groups_actions'):
			return GroupUserSerializer
		elif self.action == 'accept_invitation':
			return InvitationSerializer
		else:
			return GroupSerializer

	@swagger_auto_schema(
		responses={
			201: openapi.Response(description="Успешное создание группы", schema=GroupResponseSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
																									{"error": "string"}})
		},
		operation_summary="Создание новой группы",
		operation_description="Создает новую группу для данного пользователя.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате "
							  "'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.\n"
	)
	def create(self, request):
		user = request.user
		# проверяем тип аккаунта пользователя и количество групп, в которых он состоит
		premium_end = user.userprofile.premium_end
		premium_account = True if premium_end and premium_end >= date.today() else False
		group_number = len(user.group_users.all())
		# если у пользователя премиум аккаунт, то он может иметь не более 3 групп (не считая дефолтной группы)
		if premium_account and group_number > 3:
			return Response({"detail": {"code": "HTTP_403_FORBIDDEN", "message": "Пользователь с премиум-аккаунтом "
																	 "не может иметь больше трех групп"}}, status=403)
		# если у пользователя бесплатный аккаунт, то он может иметь не более 1 группы (не считая дефолтной группы)
		if not premium_account and group_number > 1:
			return Response({"detail": {"code": "HTTP_403_FORBIDDEN", "message": "Пользователь с бесплатным аккаунтом "
																	 "не может иметь больше одной группы"}}, status=403)
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			name = serializer.validated_data['name']
			color = serializer.validated_data['color']
			# создаем группу
			group = Group.objects.create(owner=user, name=name, color=color)
			logger.info(f"{user.username} created new group '{name}'")
			# добавляем пользователя в созданную им группу
			GroupUser.objects.create(user=user, group=group, user_name=user.first_name)
			return Response({"detail": {"code": "HTTP_201_CREATED", "message": "Группа создана"},
							            "data": GroupSerializer(group, context={'request': request}).data}, status=201)

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
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
																									{"error": "string"}})
		},
		operation_summary="Удаление группы по id",
		operation_description="Удаляет группу из базы данных по ее id и всех добавленных в нее пользователей с "
							  "неактивными профилями.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате "
							  "'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'\n"
							  "Пользователь может удалить только созданную им группу."
	)
	def destroy(self, request, pk):
		group = self.get_object()
		# получаем список участников группы
		group_users = group.users.all()
		# для каждого участника группы получаем его профиль, и если он не был активирован, то удаляем его из БД
		for group_user in group_users:
			user = group_user.user
			if not user.is_active:
				user.delete()
		# удаляем группу
		group.delete()
		logger.info(f"Group #{pk} was deleted")
		return Response(status=204)

	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный ответ", schema=GroupResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Группа не найдена", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
																									{"error": "string"}})
		},
		operation_summary="Редактирование группы по id",
		operation_description="Эндпоинт для редактирования данных группы.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате "
							  "'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'\n"
							  "Пользователь может редактировать только созданную им группу."
	)
	def partial_update(self, request, pk):
		group = self.get_object()
		serializer = self.get_serializer(data=request.data, partial=True)
		if serializer.is_valid():
			group.name = serializer.validated_data.get('name', group.name)
			group.color = serializer.validated_data.get('color', group.color)
			group.save()
			return Response(
				{"detail": {"code": "HTTP_200_OK", "message": "Группа успешно изменена"}, "data":
					GroupSerializer(group, context={'request': request}).data}, status=200)

		response = {'detail': {
			"code": "BAD_REQUEST",
			"message": serializer.errors
		}}
		return Response(response, status=status.HTTP_400_BAD_REQUEST)

	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный ответ", schema=GroupListResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
																									{"error": "string"}})
		},
		operation_summary="Получение всех групп пользователя",
		operation_description="Выводит список всех групп пользователя.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате '"
							  "Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'"
	)
	def list(self, request):
		user = request.user
		group_users = user.group_users.all().distinct('group')
		groups = [group_user.group for group_user in group_users]
		groups_data = [GroupSerializer(group, context={'request': request}).data for group in groups if not group.default]
		return Response({"detail": {"code": "HTTP_200_OK", "message": "Получен список групп пользователя"},
						 "data": groups_data}, status=200)

	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный ответ", schema=GroupUsersResponseSerializer),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Группа не найдена", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса",
								  examples={"application/json": {"error": "string"}})
		},
		operation_summary="Получение всех участников группы",
		operation_description="Выводит всех участников данной группы кроме пользователя, который сделал запрос.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате "
							  "'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.\n"
							  "Пользователь может просматривать участников только тех групп, в которых он состоит."
	)
	def retrieve(self, request, pk):
		group = self.get_object()
		user = request.user
		group_users = group.users.all()
		response = [GroupUserSerializer(group_user).data for group_user in group_users if group_user.user.id != user.id]
		return Response({"detail": {"code": "HTTP_200_OK", "message": "Получен список участников группы"},
						 "data": response}, status=200)

	@action(detail=False, methods=['get'], url_path=r'users')
	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный ответ", schema=GroupUserListResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация",
								  examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса",
								  examples={"application/json": {"error": "string"}})
		},
		operation_summary="Получение всех групп пользователя со списком участников",
		operation_description="Выводит список всех групп пользователя со списком участников.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer "
							  "3fa85f64-5717-4562-b3fc-2c963f66afa6'"
	)
	def groups_with_users(self, request):
		user = request.user
		group_users = user.group_users.all().distinct('group')
		groups = [group_user.group for group_user in group_users if not group_user.group.default]
		groupusers_data = []
		for group in groups:
			users = [GroupUserSerializer(u).data for u in group.users.all() if u.user.id != user.id]
			groupusers_data.append({'group': GroupSerializer(group, context={'request': request}).data,	'users': users})

		return Response({"detail": {"code": "HTTP_200_OK", "message": "Получен список групп пользователя"},
						 "data": groupusers_data}, status=200)


	@action(detail=True, methods=['post'])
	@swagger_auto_schema(
		responses={
			201: openapi.Response(description="Успешное добавление участника", schema=GroupUserResponseSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Группа не найдена", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
																									{"error": "string"}})
		},
		operation_summary="Добавление участника в группу",
		operation_description="Добавляет нового участника в группу.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате "
							  "'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.\n"
							  "Добавить участника может только владелец группы."
	)
	def add_user(self, request, pk):
		group = self.get_object()
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			user_name = serializer.validated_data.get('user_name')
			groupuser_data = serializer.validated_data
			# генерируем уникальное имя для нового пользователя и проверяем, что такого имени нет в БД
			for _ in range(10):
				username = f"{user_name}-{''.join(random.choices(string.ascii_letters + string.digits, k=8))}"
				if not User.objects.filter(username=username):
					break
			# сначала создаем нового пользователя
			user = User.objects.create_user(username=username)
			user.is_active = False
			user.save()
			# затем добавляем его в группу
			group_user = GroupUser.objects.create(user=user, group=group, **groupuser_data)
			logger.info(f"User {user.username} was added to group '{group.name}'")
			return Response({"detail": {"code": "HTTP_201_CREATED", "message": "Участник добавлен в группу"}, "data":
																			GroupUserSerializer(group_user).data}, status=201)

		response = {'detail': {
			"code": "BAD_REQUEST",
			"message": serializer.errors
		}}
		return Response(response, status=status.HTTP_400_BAD_REQUEST)

	@swagger_auto_schema(
		method='patch',
		responses={
			200: openapi.Response(description="Успешное редактирование данных участника", schema=GroupUserResponseSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Объект не найден", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
																									{"error": "string"}})
		},
		operation_summary="Редактирование участника группы",
		operation_description="Редактирует данные участников группы.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате "
							  "'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.\n"
							  "Редактировать участника может только владелец группы."
	)
	@swagger_auto_schema(
		method='delete',
		responses={
			204: openapi.Response(description="Успешное удаление участника из группы"),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json":
																					 {"detail": "string"}}),
			403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Объект не найден", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
																									{"error": "string"}})
		},
		operation_summary="Удаление участника из группы",
		operation_description="Удаляет участников из группы.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате "
							  "'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.\n"
							  "Удалить участника может только владелец группы."
	)
	@action(detail=True, methods=['patch', 'delete'], url_path=r'users/(?P<user_id>\d+)')
	def groups_actions(self, request, *args, **kwargs):
		if request.method == 'DELETE':
			return self.delete_group_user(request, *args, **kwargs)
		else:
			return self.update_group_user(request, *args, **kwargs)

	def update_group_user(self, request, pk, user_id):
		group_user = get_object_or_404(GroupUser, id=user_id)
		serializer = self.get_serializer(data=request.data, partial=True)
		if serializer.is_valid():
			group_user.user_name = serializer.validated_data.get('user_name', group_user.user_name)
			group_user.user_role = serializer.validated_data.get('user_role', group_user.user_role)
			group_user.user_color = serializer.validated_data.get('user_color', group_user.user_color)
			group_user.save()
			return Response({"detail": {"code": "HTTP_200_OK", "message": "Данные участника успешно отредактированы"},
							 "data": GroupUserSerializer(group_user).data}, status=200)

		response = {'detail': {
			"code": "BAD_REQUEST",
			"message": serializer.errors
		}}
		return Response(response, status=status.HTTP_400_BAD_REQUEST)

	def delete_group_user(self, request, pk, user_id):
		group_user = get_object_or_404(GroupUser, id=user_id)
		user = group_user.user
		group_user.delete()
		logger.info(f"User {user.username} was removed from group")
		if not user.is_active:
			user.delete()
		return Response(status=204)

	@action(detail=False, methods=['post'])
	@swagger_auto_schema(
		responses={
			200: openapi.Response(description="Успешный ответ", schema=ErrorResponseSerializer()),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Объект не найден", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
																									{"error": "string"}})
		},
		operation_summary="Добавление пользователя в группу по приглашению",
		operation_description="Добавляет пользователя в группу по приглашению владельца группы.\n"
							  "Меняет пользователя, созданного владельцем группы, на авторизованного пользователя.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате "
							  "'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'."
	)
	def accept_invitation(self, request):
		user = request.user
		# проверяем тип аккаунта пользователя и количество групп, в которых он состоит
		premium_end = user.userprofile.premium_end
		premium_account = True if premium_end and premium_end >= date.today() else False
		group_number = len(user.group_users.all())
		# если у пользователя премиум аккаунт, то он может иметь не более 3 групп (не считая дефолтной группы)
		if premium_account and group_number > 3:
			return Response({"detail": {"code": "HTTP_403_FORBIDDEN", "message": "Пользователь с премиум-аккаунтом не "
																		 "может иметь больше трех групп"}}, status=403)
		# если у пользователя бесплатный аккаунт, то он может иметь не более 1 группы (не считая дефолтной группы)
		if not premium_account and group_number > 1:
			return Response({"detail": {"code": "HTTP_403_FORBIDDEN", "message": "Пользователь с бесплатным аккаунтом не "
																		 "может иметь больше одной группы"}}, status=403)
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			user_id = serializer.validated_data['user_id']
			group_user = get_object_or_404(GroupUser, id=user_id)
			old_user = group_user.user
			group_user.user = user
			group_user.save()
			old_user.delete()
			return Response({"detail": {"code": "HTTP_200_OK", "message": "Приглашение в группу принято"}}, status=200)

		response = {'detail': {
			"code": "BAD_REQUEST",
			"message": serializer.errors
		}}
		return Response(response, status=status.HTTP_400_BAD_REQUEST)

	@action(detail=True, methods=['delete'])
	@swagger_auto_schema(
		responses={
			204: openapi.Response(description="Успешное удаление участника из группы"),
			400: openapi.Response(description="Ошибка при валидации входных данных", schema=ErrorResponseSerializer()),
			401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
			404: openapi.Response(description="Объект не найден", examples={"application/json": {"detail": "string"}}),
			500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
																									{"error": "string"}})
		},
		operation_summary="Выход из группы",
		operation_description="Удаляет авторизованного пользователя из группы и вместо него создает виртуального участника.\n"
							  "Условия доступа к эндпоинту: токен авторизации в формате "
							  "'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.\n"
	)
	def quit_group(self, request, pk):
		group = self.get_object()
		user = request.user
		groupuser = get_object_or_404(GroupUser, user=user, group=group)
		# генерируем уникальное имя для нового виртуального пользователя и проверяем, что такого имени нет в БД
		for _ in range(10):
			username = f"{groupuser.user_name}-{''.join(random.choices(string.ascii_letters + string.digits, k=8))}"
			if not User.objects.filter(username=username):
				break
		# сначала создаем нового виртуального пользователя
		new_user = User.objects.create_user(username=username)
		new_user.is_active = False
		new_user.save()
		# затем добавляем его в группу вместо ушедшего
		groupuser.user = new_user
		groupuser.save()
		logger.info(f"User {user.username} left the group '{group.name}'")
		return Response(status=204)


def add_default_group(request):
	""" Добавляет дефолтную группу для пользователей, у которых она отсутствует """
	users = User.objects.all()
	for user in users:
		if user.is_active:
			# создаем или получаем группу для активного пользователя
			created_group = Group.objects.get_or_create(owner=user, default=True, defaults={'name': 'default_group',
																							'color': 'default_color'})
			print(user.username, 'create group : ', created_group)
			# добавляем пользователя в группу, если он еще не добавлен
			created_groupuser = GroupUser.objects.get_or_create(user=user, group=created_group[0], defaults={'user_name': 'me'})
			print(user.username, 'create groupuser : ', created_groupuser)
	print("all done")
	return HttpResponse("It's done.")





