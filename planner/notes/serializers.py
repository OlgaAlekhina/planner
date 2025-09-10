from rest_framework import serializers
from .models import Note, Task


class NoteSerializer(serializers.ModelSerializer):
    """ Сериализатор для заметок """

    class Meta:
        model = Note
        fields = ['id', 'title', 'text', 'create_at', 'update_at']
        read_only_fields = ['id', 'create_at', 'update_at']


class TaskSerializer(serializers.ModelSerializer):
    """ Сериализатор для задач """

    class Meta:
        model = Task
        fields = ['id', 'text', 'date', 'time', 'important', 'done', 'create_at', 'update_at']
        read_only_fields = ['id', 'create_at', 'update_at']

