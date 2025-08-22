from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """ Админка для заметок """
    list_display = ['title', 'author', 'create_at', 'update_at']
