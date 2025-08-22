# serializers.py
from rest_framework import serializers
from .models import Note
from django.contrib.auth.models import User


class NoteSerializer(serializers.ModelSerializer):
    """ Сериализатор для заметок """

    class Meta:
        model = Note
        fields = ['id', 'title', 'text', 'create_at', 'update_at']
        read_only_fields = ['id', 'create_at', 'update_at']

    # def validate_title(self, value):
    #     """Allow empty title since it will be auto-generated"""
    #     return value or ''