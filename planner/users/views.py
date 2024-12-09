from django.contrib.auth.models import User
from rest_framework import viewsets, mixins, status
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.decorators import action
from .serializers import (YandexAuthSerializer,)
from .services import get_or_create_user
from rest_framework.response import Response
from rest_framework.authtoken.models import Token


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

	def get_serializer_class(self):
		if self.action == 'yandex_auth':
			return YandexAuthSerializer

	@action(detail=False, methods=['post'])
	def yandex_auth(self, request):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			oauth_token = serializer.validated_data['oauth_token']
			response_data = get_or_create_user(oauth_token)
			print(response_data)
			user_id = response_data.get('id')
			user = User.objects.get(id=user_id)
			token = Token.objects.get(user=user)
			print(token)
			response_data.update({'token': token.key})
			response = {
				"status": status.HTTP_200_OK,
				"message": "Авторизация прошла успешно",
				"data": response_data
			}
			return Response(response, status=status.HTTP_200_OK)

		return serializer.errors
