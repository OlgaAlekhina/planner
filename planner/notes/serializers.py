from django.db import transaction
from rest_framework import serializers
from .models import Note, Task, ListItem, List


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


class ListItemSerializer(serializers.ModelSerializer):
    """ Сериализатор для элементов списка """
    class Meta:
        model = ListItem
        fields = ['id', 'text', 'create_at', 'checked']
        read_only_fields = ['id', 'create_at']


class ListSerializer(serializers.ModelSerializer):
    """ Сериализатор для списков """
    items = ListItemSerializer(many=True)

    class Meta:
        model = List
        fields = ['id', 'title', 'create_at', 'update_at', 'items']
        read_only_fields = ['id', 'create_at', 'update_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        if not validated_data.get('title') and items_data:
            first_text = items_data[0]['text']
            validated_data['title'] = first_text[:47] + '...' if len(first_text) > 50 else first_text

        with transaction.atomic():
            list_obj = List.objects.create(**validated_data)

            if items_data:
                list_items = [
                    ListItem(list=list_obj, **item_data)
                    for item_data in items_data
                ]
                ListItem.objects.bulk_create(list_items)

        return list_obj

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        # Обновляем основные поля списка
        instance.title = validated_data.get('title', instance.title)
        instance.save()

        # Если переданы items, обновляем их
        if items_data is not None:
            # Удаляем старые items
            instance.items.all().delete()

            # Создаем новые
            for item_data in items_data:
                ListItem.objects.create(list=instance, **item_data)

        return instance


class PlannerResponseSerializer(serializers.Serializer):
    """ Сериализатор ответа для получения всех задач, заметок и списков пользователя """
    type = serializers.CharField()
    id = serializers.IntegerField()
    title = serializers.CharField()
    important = serializers.BooleanField()
    done = serializers.BooleanField()
    update_at = serializers.DateTimeField()


