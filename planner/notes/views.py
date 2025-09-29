from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters

from .models import Note, Task
from .paginators import TaskPagination
from .serializers import NoteSerializer, TaskSerializer
from planner.permissions import NotePermission, TaskPermission


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
            200: openapi.Response(description="Создана новая заметка", schema=NoteSerializer()),
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
            200: openapi.Response(description="Создана новая задача", schema=TaskSerializer()),
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



