from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Note(models.Model):
    """ Модель для хранения заметок """
    title = models.CharField(max_length=200, blank=True)
    text = models.TextField()
    create_at = models.DateTimeField(default=timezone.now)
    update_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # если у заметки нет названия, то берем для него первую строку из текста или первые 200 символов
        if not self.title and self.text:
            first_line = self.text.split('\n')[0]
            self.title = first_line[:200]

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-update_at']
