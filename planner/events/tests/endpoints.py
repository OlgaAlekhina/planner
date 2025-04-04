import requests
from .config import config


api_url = config.API_URL
test_user_token = config.TEST_USER_TOKEN

def test_get_event():
    r = requests.get(f'{api_url}/events/1/', headers={"Authorization": f"Bearer {test_user_token}"})
    assert r.status_code == 200