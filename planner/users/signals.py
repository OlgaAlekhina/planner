from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """ Создает профиль пользователя при создании нового пользователя"""
    if created:
        email = instance.email
        nickname = email.split('@')[0]
        UserProfile.objects.create(user=instance, nickname=nickname)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """ Обновляет пофиль пользователя при сохранении основных данных пользователя """
    instance.userprofile.save()



