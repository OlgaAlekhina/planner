from django.contrib.auth.models import User
from rest_framework import viewsets, mixins, status
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser


# аутентификация пользователя по мейлу
def authenticate_user(email, password):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None
    else:
        if user.check_password(password) and user.is_active:
            return user
    return None


# endpoints for users
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m not in ['put']]
	parser_classes = (JSONParser, MultiPartParser)
