import requests

from config import API_URL, API_KEY


class PlannerAPIClient:
    def __init__(self):
        self.base_url = API_URL
        self.api_key = API_KEY
        self.headers = {'API-key': self.api_key}

    def check_telegram_user(self, telegram_id):
        """ Проверяет, есть ли пользователь с таким Telegram ID """
        try:
            response = requests.post(
                f"{self.base_url}/check-telegram-user/",
                headers=self.headers,
                json={'telegram_id': telegram_id}
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def authenticate_user(self, email, password, telegram_id, telegram_username=None):
        """ Авторизует пользователя и привязывает Telegram ID к его аккаунту """
        try:
            response = requests.post(
                f"{self.base_url}/authenticate-user/",
                headers=self.headers,
                json={
                    'email': email,
                    'password': password,
                    'telegram_id': telegram_id,
                    'telegram_username': telegram_username,
                }
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}


# Создаем глобальный клиент
api_client = PlannerAPIClient()