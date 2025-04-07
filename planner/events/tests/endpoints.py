import requests
from .config import config


api_url = config.API_URL
test_user_token = config.TEST_USER_TOKEN

event_id = None

def test_create_event():
    global event_id
    payload = {"event_data": {
        "title": "New test",
        "location": "Moscow",
        "start_date": "2025-04-03",
        "end_date": "2025-04-03",
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


def test_delete_event():
    global event_id
    r = requests.delete(f'{api_url}/events/{event_id}/', headers={"Authorization": f"Bearer {test_user_token}"})
    assert r.status_code == 204