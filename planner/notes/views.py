from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .mixins import AutoDocMixin
from .models import Note, Task
from .serializers import NoteSerializer, TaskSerializer
from planner.permissions import NotePermission, TaskPermission


class NoteViewSet(AutoDocMixin, viewsets.ModelViewSet):
    http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated, NotePermission]

    # Переопределяем summary
    summary_mapping = {
        'list': 'Получение списка заметок',
        'create': 'Создание новой заметки',
        'retrieve': 'Получение заметки по id',
        'partial_update': 'Редактирование заметки по id',
        'destroy': 'Удаление заметки по id',
    }

    # Переопределяем description
    description_mapping = {
        'list': 'Выводит список всех заметок пользователя.\n'
                'Условия доступа к эндпоинту: токен авторизации в формате "Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6".',
        'create': 'Создает новую заметку пользователя.\n'
                  'Условия доступа к эндпоинту: токен авторизации в формате "Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6".',
        'retrieve': 'Выводит одну заметку пользователя по переданному id.\n'
                    'Условия доступа к эндпоинту: токен авторизации в формате "Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6".',
        'partial_update': 'Частичное обновление заметки. Можно обновить только отдельные поля заметки.\n'
                          'Условия доступа к эндпоинту: токен авторизации в формате "Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6".',
        'destroy': 'Удаляет заметку из базы данных.\n'
                   'Условия доступа к эндпоинту: токен авторизации в формате "Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6".',
    }

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


class TaskViewSet(AutoDocMixin, viewsets.ModelViewSet):
    http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, TaskPermission]

    # Переопределяем summary
    summary_mapping = {
        'list': 'Получение списка задач',
        'create': 'Создание новой задачи',
        'retrieve': 'Получение задачи по id',
        'partial_update': 'Редактирование задачи по id',
        'destroy': 'Удаление задачи по id',
    }

    # Переопределяем description
    description_mapping = {
        'list': 'Выводит список всех задач пользователя.\n'
                'Условия доступа к эндпоинту: токен авторизации в формате "Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6".',
        'create': 'Создает новую задачу пользователя.\n'
                  'Условия доступа к эндпоинту: токен авторизации в формате "Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6".',
        'retrieve': 'Выводит одну задачу пользователя по переданному id.\n'
                    'Условия доступа к эндпоинту: токен авторизации в формате "Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6".',
        'partial_update': 'Частичное обновление задачи. Можно обновить только отдельные поля задачи.\n'
                          'Условия доступа к эндпоинту: токен авторизации в формате "Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6".',
        'destroy': 'Удаляет задачу из базы данных.\n'
                   'Условия доступа к эндпоинту: токен авторизации в формате "Bearer 3fa85f64-5717-4562-b3fc-2c963f66afa6".',
    }

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



