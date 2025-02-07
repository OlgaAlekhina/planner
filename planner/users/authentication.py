from rest_framework import authentication


class BearerTokenAuthentication(authentication.TokenAuthentication):
    """
    меняет ключевое слово в заголовке аутентификации с Token на Bearer
    """
    keyword = 'Bearer'
