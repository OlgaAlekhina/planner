from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Note
from .serializers import NoteSerializer
from planner.permissions import NotePermission


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated, NotePermission]

    def get_queryset(self):
        """ Получаем только заметки авторизованного пользователя """
        return Note.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        """ При создании заметки делаем ее автором текущего пользователя """
        serializer.save(author=self.request.user)


