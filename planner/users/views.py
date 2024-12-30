from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins, status
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.decorators import action
from .serializers import (YandexAuthSerializer, UserLoginSerializer, LoginResponseSerializer)
from .services import get_or_create_user
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import UserProfile
from django.http import JsonResponse, HttpResponse


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
		else:
			return UserLoginSerializer

	@action(detail=False, methods=['post'])
	@swagger_auto_schema(responses={200: LoginResponseSerializer()},
						 operation_summary="Авторизация пользователей через Яндекс")
	def yandex_auth(self, request):
		serializer = self.get_serializer(data=request.data)
		if serializer.is_valid():
			oauth_token = serializer.validated_data['oauth_token']
			response_data = get_or_create_user(oauth_token)
			print(response_data)
			if response_data[1] == 200:
				response_data = response_data[0]
				user_id = response_data.get('id')
				user = User.objects.get(id=user_id)
				token = Token.objects.get(user=user)
				response = {
					"status": status.HTTP_200_OK,
					"message": "Авторизация прошла успешно",
					"data": {"user_data": response_data, "user_auth_token": token.key}
				}
				return Response(response, status=status.HTTP_200_OK)
			return Response(response_data[0], status=response_data[1])

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def add_missing_profiles(request):
	users = User.objects.all()
	for user in users:
		created = UserProfile.objects.get_or_create(user=user)
		print(user.username, ' : ', created)
	print("all done")
	return HttpResponse("It's done.")