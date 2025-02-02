from rest_framework import serializers
import re
from django.contrib.auth.models import User


def validate_password_symbols(password):
    """ Проверяет наличие недопустимых символов в пароле """
    password_pattern = '^[a-zA-Z0-9!#.$%&+=?^_`{|}~-]{2,}$'
    if re.search(password_pattern, password):
        return password
    else:
        raise serializers.ValidationError("Пароль содержит недопустимые символы")


def validate_email(email):
    """ Проверяет почтовый адрес на соответствие заданному формату """
    email_pattern = '^([a-zA-Z0-9!#.$%&+=?^_`{|}~-]+@[a-zA-Z0-9.-]+[a-zA-Z0-9]+\.[a-zA-Z]{2,})$'
    if re.search(email_pattern, email):
        return email
    else:
        raise serializers.ValidationError("Некорректный адрес электронной почты")


def check_email(email):
    """ При регистрации бросает ошибку, если email существует в БД, или удаляет аккаунт с таким email, если он не был активирован """
    user = User.objects.filter(email=email).first()
    if user.is_active:
        raise serializers.ValidationError("Пользователь с таким email адресом уже зарегистрирован в приложении")
    if user:
        user.delete()
    return email


