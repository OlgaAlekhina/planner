import requests
from .config import config
from datetime import date, timedelta

api_url = config.API_URL
test_user_token = config.TEST_USER_TOKEN
yandex_token = config.YANDEX_TOKEN

event_id = None
test_token = None

def test_yandex_auth():
    global test_token
    payload = {
      "oauth_token": yandex_token
    }
    r = requests.post(f'{api_url}/users/yandex_auth/', json=payload)
    test_token = r.json().get('data').get('user_auth_token')
    assert r.status_code == 200


def test_create_event():
    global event_id
    today = str(date.today())
    payload = {"event_data": {
        "title": "New test",
        "location": "Moscow",
        "start_date": today,
        "end_date": today,
        "start_time": "14:00:00",
        "end_time": "16:00:00"
    }}
    r = requests.post(f'{api_url}/events/', headers={"Authorization": f"Bearer {test_user_token}"}, json=payload)
    event_id = r.json().get('data').get('event_data').get('id')
    assert r.status_code == 201


def test_get_event():
    global event_id
    r = requests.get(f'{api_url}/events/{event_id}/', headers={"Authorization": f"Bearer {test_user_token}"})
    assert r.status_code == 200


def test_patch_event():
    global event_id
    tomorrow = str(date.today() + timedelta(days=1))
    payload = {"event_data": {
        "title": "Updated test",
        "location": "New_Vasyuki",
        "end_date": tomorrow
    }}
    r = requests.patch(f'{api_url}/events/{event_id}/', headers={"Authorization": f"Bearer {test_user_token}"}, json=payload)
    assert r.status_code == 200


def test_delete_event():
    global event_id
    r = requests.delete(f'{api_url}/events/{event_id}/', headers={"Authorization": f"Bearer {test_user_token}"})
    assert r.status_code == 204