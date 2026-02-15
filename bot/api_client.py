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
                f"{self.base_url}/users/check_telegram_user/",
                headers=self.headers,
                json={'telegram_id': telegram_id}
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def check_email(self, email):
        """ Проверяем, что пользователь с таким email существует в БД и отправляем ему код в письме """
        try:
            response = requests.post(
                f"{self.base_url}/users/check_mail/", headers=self.headers, json={'email': email}
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def authenticate_user(self, email, code, telegram_id):
        """ Проверяет код и привязывает Telegram ID пользователя к его аккаунту """
        try:
            response = requests.post(
                f"{self.base_url}/users/telegram_auth/",
                headers=self.headers,
                json={'email': email, 'code': code, 'telegram_id': telegram_id}
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}

    def create_event(self, user_id, title, date, time):
        """ Создание нового события """
        try:
            response = requests.post(
                f"{self.base_url}/events/create_from_telegram/",
                headers=self.headers,
                json={'author': user_id, 'title': title, 'start_date': date, 'start_time': time}
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}


# Создаем глобальный клиент
api_client = PlannerAPIClient()