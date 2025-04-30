import os
from dotenv import load_dotenv

load_dotenv()


class Config:
	API_URL = os.getenv('API_URL')
	API_URL_PROD = os.getenv('API_URL_PROD')
	YANDEX_TOKEN = os.getenv('YANDEX_TOKEN')


config = Config()