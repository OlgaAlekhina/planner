from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Note, Task, List, ListItem
from .paginators import TaskPagination
from .serializers import NoteSerializer, TaskSerializer, ListSerializer, ListItemSerializer, PlannerResponseSerializer
from planner.permissions import NotePermission, TaskPermission
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


class NoteViewSet(viewsets.ModelViewSet):
    http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated, NotePermission]
    pagination_class = TaskPagination

    def get_queryset(self):
        """ Получаем только заметки авторизованного пользователя """
        # Проверяем, не генерируется ли схема Swagger
        if getattr(self, 'swagger_fake_view', False):
            # Возвращаем пустой queryset для генерации схемы
            return Note.objects.none()

        # Для реальных запросов возвращаем отфильтрованный queryset
        return Note.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        """ При создании заметки делаем ее автором текущего пользователя """
        serializer.save(author=self.request.user)

    @swagger_auto_schema(
        operation_summary="Получение списка заметок",
        operation_description="Выводит список всех заметок пользователя с сортировкой по дате изменения или создания.\n"
                              "Есть возможность использовать постраничный вывод результатов.\n"
                              "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            200: openapi.Response(description="Получен список заметок пользователя", schema=NoteSerializer(many=True)),
            **COMMON_RESPONSES
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание новой заметки",
        operation_description="Создает новую заметку пользователя.\n"
                              "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            201: openapi.Response(description="Создана новая заметка", schema=NoteSerializer()),
            **COMMON_RESPONSES
        }
    )
    def create(self, request, *args, **kwargs):
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


class TaskViewSet(viewsets.ModelViewSet):
    http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, TaskPermission]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['done']
    pagination_class = TaskPagination

    def get_queryset(self):
        """ Получаем только задачи авторизованного пользователя """
        # Проверяем, не генерируется ли схема Swagger
        if getattr(self, 'swagger_fake_view', False):
            # Возвращаем пустой queryset для генерации схемы
            return Task.objects.none()

        # Для реальных запросов возвращаем отфильтрованный queryset
        return Task.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        """ При создании задачи делаем ее автором текущего пользователя """
        serializer.save(author=self.request.user)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'done',
                openapi.IN_QUERY,
                description="Фильтрация по статусу задач (сделаны или нет)",
                type=openapi.TYPE_BOOLEAN
            )
        ],
        operation_summary="Получение списка задач",
        operation_description="Выводит список всех задач пользователя с сортировкой сперва по дате, затем по важности, затем по времени.\n"
                "Можно фильтровать задачи по статусу (сделанные, не сделанные, все задачи).\n"
                "Есть возможность использовать постраничный вывод результатов.\n"
                "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            200: openapi.Response(description="Получен список задач пользователя", schema=TaskSerializer(many=True)),
            ** COMMON_RESPONSES
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание новой задачи",
        operation_description="Создает новую задачу пользователя.\n"
            "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            201: openapi.Response(description="Создана новая задача", schema=TaskSerializer()),
            **COMMON_RESPONSES
        }
    )
    def create(self, request, *args, **kwargs):
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


class ListViewSet(viewsets.ModelViewSet):
    http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
    permission_classes = [IsAuthenticated, TaskPermission]
    pagination_class = TaskPagination

    def get_serializer_class(self):
        if self.action in ('list_items_actions', 'create_item'):
            return ListItemSerializer
        else:
            return ListSerializer

    def get_queryset(self):
        """ Получаем только списки авторизованного пользователя """
        # Проверяем, не генерируется ли схема Swagger
        if getattr(self, 'swagger_fake_view', False):
            # Возвращаем пустой queryset для генерации схемы
            return List.objects.none()

        # Для реальных запросов возвращаем отфильтрованный queryset
        return List.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        """ При создании списка делаем его автором текущего пользователя """
        serializer.save(author=self.request.user)

    @swagger_auto_schema(
        operation_summary="Получение списков пользователя",
        operation_description="Выводит все списки пользователя с сортировкой по дате.\n"
                "Есть возможность использовать постраничный вывод результатов.\n"
                "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            200: openapi.Response(description="Получены списки пользователя", schema=ListSerializer(many=True)),
            ** COMMON_RESPONSES
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание нового списка",
        operation_description="Создает новый список пользователя.\n"
            "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            201: openapi.Response(description="Создан новый список", schema=ListSerializer()),
            **COMMON_RESPONSES
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получение списка по id",
        operation_description="Выводит один список пользователя по переданному id.\n"
            "Условия доступа к эндпоинту: токен авторизации в формате 'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.",
        responses={
            200: openapi.Response(description="Получен список", schema=TaskSerializer()),
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
            200: openapi.Response(description="Список обновлен", schema=TaskSerializer()),
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


class PlannerView(APIView):
    """ Эндпоинт для получения всех задач, заметок и списков пользователя """

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                schema=PlannerResponseSerializer(many=True)
            ),
            **COMMON_RESPONSES,
        },
        operation_summary="Получение всех задач, заметок, списков пользователя",
        operation_description="Выводит все задачи, заметки и списки авторизованного пользователя.\n"
                              "Условия доступа к эндпоинту: токен авторизации в формате "
                              "'Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6'.\n",
        tags=['planner'],
    )
    def get(self, request):
        user = self.request.user
        all_items = []

        user_tasks = Task.objects.filter(author=user)
        for task in user_tasks:
            all_items.append({
                'type': 'task',
                'id': task.id,
                'title': task.text,
                'important': task.important,
                'done': task.done,
                'update_at': task.update_at,
            })

        user_notes = Note.objects.filter(author=user)
        for note in user_notes:
            all_items.append({
                'type': 'note',
                'id': note.id,
                'title': note.title,
                'important': False,
                'done': False,
                'update_at': note.update_at,
            })

        user_lists = List.objects.filter(author=user)
        for list in user_lists:
            all_items.append({
                'type': 'list',
                'id': list.id,
                'title': list.title,
                'important': False,
                'done': False,
                'update_at': list.update_at,
            })

        return Response(sorted(all_items, key=lambda item: item['update_at'], reverse=True), status=200)



