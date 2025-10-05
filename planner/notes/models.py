import re

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Note(models.Model):
    """ Модель для хранения заметок """
    title = models.CharField('Заголовок заметки', max_length=200, blank=True)
    text = models.TextField('Текст заметки')
    create_at = models.DateTimeField('Когда создана', default=timezone.now)
    update_at = models.DateTimeField('Когда изменена', auto_now=True)
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


class Task(models.Model):
    """ Модель для хранения задач """
    text = models.TextField('Текст задачи')
    date = models.DateField('Дата в формате "2025-09-14"', blank=True, null=True)
    time = models.TimeField('Время в формате "18:30:00"', blank=True, null=True)
    important = models.BooleanField('Важная или нет', default=False)
    done = models.BooleanField('Сделана или нет', default=False)
    create_at = models.DateTimeField('Когда создана', default=timezone.now)
    update_at = models.DateTimeField('Когда изменена', auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['date', '-important', 'time']


class List(models.Model):
    """ Модель для хранения списков """
    title = models.CharField('Название списка', max_length=200, blank=True)
    create_at = models.DateTimeField('Когда создан', default=timezone.now)
    update_at = models.DateTimeField('Когда изменен', auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-update_at']


class ListItem(models.Model):
    """ Модель для хранения элементов списков """
    text = models.CharField('Текст', max_length=200)
    create_at = models.DateTimeField('Когда создан', default=timezone.now)
    checked = models.BooleanField('Отмечен или нет', default=False)
    list = models.ForeignKey(List, on_delete=models.CASCADE)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['create_at']
