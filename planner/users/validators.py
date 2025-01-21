from rest_framework import serializers
import re
from django.contrib.auth.models import User


# validator for password symbols
def validate_password_symbols(password):
    password_pattern = '^[a-zA-Z0-9!#.$%&+=?^_`{|}~-]{2,}$'
    if re.search(password_pattern, password):
        return password
    else:
        raise serializers.ValidationError("Пароль содержит недопустимые символы")


# validator for email format
def validate_email(email):
    email_pattern = '^([a-zA-Z0-9!#.$%&+=?^_`{|}~-]+@[a-zA-Z0-9.-]+[a-zA-Z0-9]+\.[a-zA-Z]{2,})$'
    if re.search(email_pattern, email):
        return email
    else:
        raise serializers.ValidationError("Некорректный адрес электронной почты")


# on registration raise error if email exists
def check_email(email):
    user = User.objects.filter(email=email).first()
    if user:
        raise serializers.ValidationError("Пользователь с таким email адресом уже зарегистрирован в приложении")
    else:
        return email