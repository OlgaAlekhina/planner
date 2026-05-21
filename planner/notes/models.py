from io import BytesIO

from PIL import Image
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone

from users.models import GroupUser


class Note(models.Model):
    """ Модель для хранения заметок """
    title = models.CharField('Заголовок заметки', max_length=200, blank=True)
    text = models.TextField('Текст заметки')
    create_at = models.DateTimeField('Когда создана', default=timezone.now)
    update_at = models.DateTimeField('Когда изменена', auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    users = models.ManyToManyField(GroupUser, blank=True, verbose_name='С кем поделились', related_name='shared_notes')

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
    users = models.ManyToManyField(GroupUser, blank=True, verbose_name='С кем поделились', related_name='shared_tasks')

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['date', '-important', 'time']
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'


class List(models.Model):
    """ Модель для хранения списков """
    title = models.CharField('Название списка', max_length=200, blank=True)
    create_at = models.DateTimeField('Когда создан', default=timezone.now)
    update_at = models.DateTimeField('Когда изменен', auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    users = models.ManyToManyField(GroupUser, blank=True, verbose_name='С кем поделились', related_name='shared_lists')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-update_at']
        verbose_name = 'Список'
        verbose_name_plural = 'Списки'


class ListItem(models.Model):
    """ Модель для хранения элементов списков """
    text = models.CharField('Текст', max_length=200)
    create_at = models.DateTimeField('Когда создан', default=timezone.now)
    checked = models.BooleanField('Отмечен или нет', default=False)
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='items')

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['create_at']


class RecipeCategory(models.Model):
    """ Модель для хранения категорий рецептов """
    name = models.CharField('Название', max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    default = models.BooleanField('Общая', default=False)
    icon = models.CharField('Иконка', max_length=200, blank=True, null=True)
    #users = models.ManyToManyField(GroupUser, blank=True, verbose_name='С кем поделились', related_name='shared_categories')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['default']
        verbose_name = 'Категория рецептов'
        verbose_name_plural = 'Категории рецептов'


class Recipe(models.Model):
    """ Модель для хранения рецептов """
    title = models.CharField('Название', max_length=500)
    text = models.TextField('Описание', blank=True, null=True)
    image = models.ImageField('Фото', upload_to='recipes/', blank=True, null=True)
    default = models.BooleanField('Общий', default=False)
    category = models.ForeignKey(RecipeCategory, on_delete=models.CASCADE, blank=True, null=True, related_name='recipes',
                                 verbose_name='Категория рецептов')
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    users = models.ManyToManyField(GroupUser, blank=True, verbose_name='С кем поделились', related_name='shared_recipes')
    create_at = models.DateTimeField('Когда создан', default=timezone.now)
    update_at = models.DateTimeField('Когда изменен', auto_now=True)
    link = models.URLField('Ссылка на рецепт', blank=True, null=True)
    favorites = models.ManyToManyField(User, blank=True, verbose_name='В избранном', related_name='favorites')

    class Meta:
        ordering = ['-update_at']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """ Оптимизация изображения перед сохранением """
        if self.image and self._state.adding:  # Только для новых записей
            self.optimize_image()
        super().save(*args, **kwargs)

    def optimize_image(self, quality=85, max_width=1200, max_height=1200):
        """ Оптимизация размера и качества изображения """
        try:
            img = Image.open(self.image)

            # Конвертация в RGB если нужно (для PNG с альфа-каналом)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            # Изменение размера с сохранением пропорций
            if img.width > max_width or img.height > max_height:
                ratio = min(max_width / img.width, max_height / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # Сохранение оптимизированного изображения
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)

            # Замена файла
            name = self.image.name.rsplit('.', 1)[0] + '.jpg'
            self.image.save(name, ContentFile(output.read()), save=False)

        except Exception as e:
            print(f"Ошибка оптимизации: {e}")
