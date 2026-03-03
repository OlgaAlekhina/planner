from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Note, Task, List, ListItem, RecipeCategory
from .paginators import TaskPagination
from .serializers import (NoteSerializer, TaskSerializer, ListSerializer, ListItemSerializer, PlannerResponseSerializer,
    PlannerSharingSerializer, RecipeCategorySerializer)
from planner.permissions import NotesPermission, RecipeCategoryPermission
from users.users_serializers import ErrorResponseSerializer


COMMON_RESPONSES = {
    401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
    500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
                                                                                            {"error": "string"}})
}

OBJECT_RESPONSES = {
    403: openapi.Response(description="Доступ запрещен", examples={"application/json": {"detail": "string"}}),
    404: openapi.Response(description="Объект не найден", examples={"application/json": {"detail": "string"}}),
}


class NoteViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated, NotesPermission]
    pagination_class = TaskPagination
    queryset = Note.objects.all()

    def perform_create(self, serializer):
        """ При создании заметки делаем ее автором текущего пользователя """
        serializer.save(author=self.request.user)

    @swagger_auto_schema(
        operation_summary="Создание новой заметки",
        operation_description="Создает новую заметку пользователя.\n"
                              "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            201: openapi.Response(description="Создана новая заметка", schema=NoteSerializer()),
            429: openapi.Response(description="Достигнут лимит заметок", examples={"application/json": {"detail": "string"}}),
            **COMMON_RESPONSES
        }
    )
    def create(self, request, *args, **kwargs):
        if Note.objects.filter(author=self.request.user).count() >= 100:
            return Response({"detail": "Достигнут лимит заметок для данного аккаунта"}, 429)
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получение заметки по id",
        operation_description="Выводит одну заметку пользователя по переданному id.\n"
                              "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            200: openapi.Response(description="Получена заметка", schema=NoteSerializer()),
            **COMMON_RESPONSES,
            **OBJECT_RESPONSES
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Редактирование заметки по id",
        operation_description="Частичное обновление заметки. Можно обновить только отдельные поля заметки.\n"
                              "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            200: openapi.Response(description="Заметка изменена", schema=NoteSerializer()),
            **COMMON_RESPONSES,
            **OBJECT_RESPONSES
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление заметки по id",
        operation_description="Удаляет заметку из базы данных.\n"
                              "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            204: openapi.Response(description="Заметка удалена"),
            **COMMON_RESPONSES,
            **OBJECT_RESPONSES
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class TaskViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, NotesPermission]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['done']
    pagination_class = TaskPagination
    queryset = Task.objects.all()

    def perform_create(self, serializer):
        """ При создании задачи делаем ее автором текущего пользователя """
        serializer.save(author=self.request.user)

    @swagger_auto_schema(
        operation_summary="Создание новой задачи",
        operation_description="Создает новую задачу пользователя.\n"
            "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            201: openapi.Response(description="Создана новая задача", schema=TaskSerializer()),
            429: openapi.Response(description="Достигнут лимит задач", examples={"application/json": {"detail": "string"}}),
            **COMMON_RESPONSES
        }
    )
    def create(self, request, *args, **kwargs):
        if Task.objects.filter(author=self.request.user).count() >= 100:
            return Response({"detail": "Достигнут лимит задач для данного аккаунта"}, 429)
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получение задачи по id",
        operation_description="Выводит одну задачу пользователя по переданному id.\n"
            "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            200: openapi.Response(description="Получена задача", schema=TaskSerializer()),
            **COMMON_RESPONSES,
            **OBJECT_RESPONSES
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Редактирование задачи по id",
        operation_description="Частичное обновление задачи. Можно обновить только отдельные поля задачи.\n"
            "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            200: openapi.Response(description="Задача изменена", schema=TaskSerializer()),
            **COMMON_RESPONSES,
            **OBJECT_RESPONSES
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление задачи по id",
        operation_description="Удаляет задачу из базы данных.\n"
                "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            204: openapi.Response(description="Задача удалена"),
            **COMMON_RESPONSES,
            **OBJECT_RESPONSES
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ListViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
    permission_classes = [IsAuthenticated, NotesPermission]
    pagination_class = TaskPagination
    queryset = List.objects.all()

    def get_serializer_class(self):
        if self.action in ('list_items_actions', 'create_item'):
            return ListItemSerializer
        else:
            return ListSerializer

    def perform_create(self, serializer):
        """ При создании списка делаем его автором текущего пользователя """
        serializer.save(author=self.request.user)

    @swagger_auto_schema(
        operation_summary="Создание нового списка",
        operation_description="Создает новый список пользователя.\n"
            "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            201: openapi.Response(description="Создан новый список", schema=ListSerializer()),
            429: openapi.Response(description="Достигнут лимит списков", examples={"application/json": {"detail": "string"}}),
            **COMMON_RESPONSES
        }
    )
    def create(self, request, *args, **kwargs):
        if List.objects.filter(author=self.request.user).count() >= 100:
            return Response({"detail": "Достигнут лимит списков для данного аккаунта"}, 429)
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получение списка по id",
        operation_description="Выводит один список пользователя по переданному id.\n"
            "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            200: openapi.Response(description="Получен список", schema=ListSerializer()),
            **COMMON_RESPONSES,
            **OBJECT_RESPONSES
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Редактирование списка по id",
        operation_description="Частичное обновление списка. Можно обновить только отдельные поля списка.\n"
                              "Если поле items не пустое, то его элементы полностью заменяют старые элементы списка.\n"
            "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            200: openapi.Response(description="Список обновлен", schema=ListSerializer()),
            **COMMON_RESPONSES,
            **OBJECT_RESPONSES
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление списка по id",
        operation_description="Удаляет список из базы данных.\n"
                "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            204: openapi.Response(description="Список удален"),
            **COMMON_RESPONSES,
            **OBJECT_RESPONSES
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method='patch',
        responses={
            200: openapi.Response(description="Успешное редактирование элемента списка", schema=ListItemSerializer()),
            **COMMON_RESPONSES,
            **OBJECT_RESPONSES
        },
        operation_summary="Редактирование элемента списка",
        operation_description="Редактирует элемент списка по переданному id.\n"
                              "Условия доступа к эндпоинту: токен авторизации в формате "
                              "'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.\n"
                              "Редактировать список может только его автор."
    )
    @swagger_auto_schema(
        method='delete',
        responses={
            204: openapi.Response(description="Успешное удаление элемента списка"),
            **COMMON_RESPONSES,
            **OBJECT_RESPONSES
        },
        operation_summary="Удаление элемента списка",
        operation_description="Удаляет элемент списка.\n"
                              "Условия доступа к эндпоинту: токен авторизации в формате "
                              "'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.\n"
                              "Удалить элемент списка может только его автор."
    )
    @action(detail=True, methods=['patch', 'delete'], url_path=r'items/(?P<item_id>\d+)')
    def list_items_actions(self, request, *args, **kwargs):
        # вызываем этот метод, чтобы проверить права пользователя на объект
        self.get_object()
        if request.method == 'DELETE':
            return self.delete_item(request, *args, **kwargs)
        else:
            return self.update_item(request, *args, **kwargs)

    def update_item(self, request, pk, item_id):
        list_item = get_object_or_404(ListItem, id=item_id)
        serializer = self.get_serializer(data=request.data, partial=True)
        if serializer.is_valid():
            list_item.text = serializer.validated_data.get('text', list_item.text)
            list_item.checked = serializer.validated_data.get('checked', list_item.checked)
            list_item.save()
            return Response(ListItemSerializer(list_item).data, status=200)

        response = {'detail': {
            "code": "BAD_REQUEST",
            "message": serializer.errors
        }}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def delete_item(self, request, pk, item_id):
        list_item = get_object_or_404(ListItem, id=item_id)
        list_item.delete()
        return Response(status=204)

    @action(detail=True, methods=['post'], url_path='items')
    @swagger_auto_schema(
        responses={
            201: openapi.Response(description="Успешное создание элемента списка", schema=ListItemSerializer()),
            **COMMON_RESPONSES
        },
        operation_summary="Создание элемента списка",
        operation_description="Создает элемент списка.\n"
                              "Условия доступа к эндпоинту: токен авторизации в формате "
                              "'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.\n"
    )
    def create_item(self, request, pk=None):
        user_list = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            new_item = ListItem.objects.create(list=user_list, **serializer.validated_data)
            return Response(ListItemSerializer(new_item).data, status=201)

        response = {'detail': {
            "code": "BAD_REQUEST",
            "message": serializer.errors
        }}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class RecipeCategoryViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin, viewsets.GenericViewSet):
    http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
    permission_classes = [IsAuthenticated, RecipeCategoryPermission]
    queryset = RecipeCategory.objects.all()
    serializer_class = RecipeCategorySerializer

    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Успешный ответ", schema=RecipeCategorySerializer(many=True)),
            401: openapi.Response(description="Требуется авторизация", examples={"application/json": {"detail": "string"}}),
            500: openapi.Response(description="Ошибка сервера при обработке запроса", examples={"application/json":
                                                                                                    {"error": "string"}})
        },
        operation_summary="Получение всех категорий рецептов пользователя",
        operation_description="Выводит список всех категорий рецептов пользователя (общих и личных).\n"
                              "Условия доступа к эндпоинту: токен авторизации в формате '"
                              "Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'"
    )
    def list(self, request):
        user = request.user
        # Получаем список group_users для данного пользователя
        group_users = user.group_users.all()
        # Получаем все категории, если пользователь их автор или с ним поделились или это общие категории
        recipe_categories = RecipeCategory.objects.filter(Q(author=user) | Q(users__in=group_users) | Q(default=True)).distinct()
        return Response(RecipeCategorySerializer(recipe_categories, many=True).data, status=200)

    def perform_create(self, serializer):
        """ При создании категории делаем ее автором текущего пользователя """
        serializer.save(author=self.request.user)

    @swagger_auto_schema(
        operation_summary="Создание новой категории рецептов",
        operation_description="Создает новую категорию рецептов для пользователя.\n"
                              "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            201: openapi.Response(description="Создана новая категория рецептов", schema=RecipeCategorySerializer()),
            **COMMON_RESPONSES
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Редактирование категории рецептов по id",
        operation_description="Изменение названия категории рецептов.\n"
                              "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            200: openapi.Response(description="Категория изменена", schema=RecipeCategorySerializer()),
            **COMMON_RESPONSES,
            **OBJECT_RESPONSES
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление категории рецептов по id",
        operation_description="Удаляет категорию рецептов из базы данных.\n"
                              "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            204: openapi.Response(description="Категория удалена"),
            **COMMON_RESPONSES,
            **OBJECT_RESPONSES
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class PlannerView(APIView):
    """ Эндпоинт для получения всех задач, заметок и списков пользователя """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'type',
                openapi.IN_QUERY,
                description="Item's type: task, note or list",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=PlannerResponseSerializer(many=True)
            ),
            **COMMON_RESPONSES,
        },
        operation_summary="Получение всех задач, заметок, списков пользователя",
        operation_description="Выводит все задачи, заметки и списки авторизованного пользователя с возможностью "
              "фильтрации по типу: 'task', 'note', 'list'.\n"
              "Поле 'title' содержит заголовок для заметок и списков и текст для задач.\n"
              "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.\n",
        tags=['planner'],
    )
    def get(self, request):
        user = self.request.user
        item_type = request.GET.get('type', '')
        all_items = []

        if not item_type or item_type == 'task':
            # Получаем список group_users для данного пользователя
            group_users = user.group_users.all()
            # Получаем все задачи, если пользователь их автор или с ним поделились
            user_tasks = Task.objects.filter(Q(author=user) | Q(users__in=group_users)).distinct()
            for task in user_tasks:
                all_items.append({
                    'type': 'task',
                    'id': task.id,
                    'title': task.text,
                    'date': task.date,
                    'time': task.time,
                    'important': task.important,
                    'done': task.done,
                    'update_at': task.update_at,
                })

        if not item_type or item_type == 'note':
            # Получаем список group_users для данного пользователя
            group_users = user.group_users.all()
            # Получаем все заметки, если пользователь их автор или с ним поделились
            user_notes = Note.objects.filter(Q(author=user) | Q(users__in=group_users)).distinct()
            for note in user_notes:
                all_items.append({
                    'type': 'note',
                    'id': note.id,
                    'title': note.title,
                    'date': None,
                    'time': None,
                    'important': False,
                    'done': False,
                    'update_at': note.update_at,
                })

        if not item_type or item_type == 'list':
            # Получаем список group_users для данного пользователя
            group_users = user.group_users.all()
            # Получаем все заметки, если пользователь их автор или с ним поделились
            user_lists = List.objects.filter(Q(author=user) | Q(users__in=group_users)).distinct()
            for list in user_lists:
                all_items.append({
                    'type': 'list',
                    'id': list.id,
                    'title': list.title,
                    'date': None,
                    'time': None,
                    'important': False,
                    'done': False,
                    'update_at': list.update_at,
                })

        return Response(sorted(all_items, key=lambda item: item['update_at'], reverse=True), status=200)


class PlannerSharingView(APIView):
    """ Эндпоинт для шаринга задач, заметок и списков с другими пользователями """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=PlannerSharingSerializer(),
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=ErrorResponseSerializer()
            ),
            **COMMON_RESPONSES,
            **OBJECT_RESPONSES
        },
        operation_summary="Поделиться задачей, заметкой или списком с другими пользователями",
        operation_description="Выдает указанным пользователям все права на заметку, задачу или список.\n\n"
              "Возможные значения поля 'item_type': 'task', 'note', 'list'.\n\n"
              "Поле 'users_list' содержит список групповых ID пользователей, которым надо выдать права.\n\n"
              "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        tags=['planner'],
    )
    def patch(self, request, item_id):
        data = request.data
        serializer = PlannerSharingSerializer(data=data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        item_type = serializer.validated_data['item_type']
        users_list = serializer.validated_data['users_list']

        types_dict = {
            'task': Task,
            'note': Note,
            'list': List,
        }

        try:
            item = types_dict[item_type].objects.get(id=item_id)
        except:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        for group_user in users_list:
            item.users.add(group_user)

        return Response({"detail": {"code": "HTTP_200_OK", "message": "Successfully updated item"}},
                                                                                    status=status.HTTP_200_OK)

def main_page(request):
    """Главная страница - статичный лендинг"""
    return render(request, 'index.html')


