import os
from dotenv import load_dotenv

load_dotenv()

class Config:
	API_URL = os.getenv('API_URL')
	TEST_USER_TOKEN = os.getenv('TEST_USER_TOKEN')

config = Config()