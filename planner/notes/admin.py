from django.contrib import admin
from django.utils.html import strip_tags
from django.utils.text import Truncator

from .models import Note, Task


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """ Админка для заметок """
    list_display = ['title', 'author', 'create_at', 'update_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """ Админка для задач """
    list_display = ['short_text_display', 'author', 'create_at', 'update_at']

    def short_text_display(self, obj):
        clean_text = strip_tags(obj.text)
        return Truncator(clean_text).chars(60, truncate='...')

    short_text_display.short_description = 'Текст'
