# тестовые запросы к апи для работы с пользователями, группами и событиями


import requests
import pytest
from .config import config
from datetime import date, timedelta

api_url = config.API_URL
api_url_prod = config.API_URL_PROD
yandex_token = config.YANDEX_TOKEN

event_id = None
test_user_token = None
test_user_id = None
group_id = None
group_user_id = None


@pytest.fixture
def base_url(request):
    """ Определяет, по какому урлу делать запросы, в зависимости от значения флага --env в команде pytest """
    env_param = request.config.getoption('--env')
    base_url = api_url_prod if env_param == 'prod' else api_url
    return base_url


def test_yandex_auth(base_url):
    """ Авторизация тестового пользователя через Яндекс """
    global test_user_token
    global test_user_id
    payload = {
      "oauth_token": yandex_token
    }
    r = requests.post(f'{base_url}/users/yandex_auth/', json=payload)
    test_user_token = r.json().get('data').get('user_auth_token')
    test_user_id = r.json().get('data').get('user_data').get('id')
    assert r.status_code == 200


def test_get_user(base_url):
    """ Получение данных тестового пользователя """
    global test_user_id
    global test_user_token
    r = requests.get(f'{base_url}/users/{test_user_id}/', headers={"Authorization": f"Bearer {test_user_token}"})
    assert r.status_code == 200


def test_patch_user(base_url):
    """ Изменение профиля тестового пользователя """
    global event_id
    global test_user_token
    payload = {"first_name": "Olga"}
    r = requests.patch(f'{base_url}/users/{test_user_id}/', headers={"Authorization": f"Bearer {test_user_token}"}, json=payload)
    assert r.status_code == 200
    assert r.json().get('data').get('first_name') == 'Olga'


def test_create_group(base_url):
    """ Создание тестовой группы """
    global group_id
    global test_user_token
    payload = {
        "name": "Test group",
        "color": "some color"
    }
    r = requests.post(f'{base_url}/groups/', headers={"Authorization": f"Bearer {test_user_token}"}, json=payload)
    group_id = r.json().get('data').get('id')
    assert r.status_code == 201


def test_create_second_group(base_url):
    """ Создание второй тестовой группы (запрещено для пользователя с бесплатным аккаунтом) """
    global test_user_token
    payload = {
        "name": "Test group 2",
        "color": "some color"
    }
    r = requests.post(f'{base_url}/groups/', headers={"Authorization": f"Bearer {test_user_token}"}, json=payload)
    assert r.status_code == 403


def test_patch_group(base_url):
    """ Изменение данных группы """
    global group_id
    global test_user_token
    payload = {"name": "My family"}
    r = requests.patch(f'{base_url}/groups/{group_id}/', headers={"Authorization": f"Bearer {test_user_token}"}, json=payload)
    assert r.status_code == 200
    assert r.json().get('data').get('name') == 'My family'


def test_add_group_user(base_url):
    """ Добавление участника в группу """
    global group_id
    global test_user_token
    global group_user_id
    payload = {
        "user_name": "Kisa",
        "user_role": "my sweetheart"
    }
    r = requests.post(f'{base_url}/groups/{group_id}/add_user/', headers={"Authorization": f"Bearer {test_user_token}"},
                      json=payload)
    group_user_id = r.json().get('data').get('id')
    assert r.status_code == 201


def test_patch_group_user(base_url):
    """ Изменение данных участника группы """
    global group_id
    global test_user_token
    global group_user_id
    payload = {"user_name": "Osya"}
    r = requests.patch(f'{base_url}/groups/{group_id}/users/{group_user_id}/',
                       headers={"Authorization": f"Bearer {test_user_token}"}, json=payload)
    assert r.status_code == 200
    assert r.json().get('data').get('user_name') == 'Osya'


def test_get_groups(base_url):
    """ Получение всех групп тестового пользователя """
    global test_user_token
    r = requests.get(f'{base_url}/groups/', headers={"Authorization": f"Bearer {test_user_token}"})
    assert r.status_code == 200
    assert len(r.json().get('data')) == 1


def test_get_groups_with_users(base_url):
    """ Получение всех групп тестового пользователя со списком участников """
    global test_user_token
    r = requests.get(f'{base_url}/groups/users/', headers={"Authorization": f"Bearer {test_user_token}"})
    assert r.status_code == 200
    assert r.json().get('data')[0].get('group').get('name') == "My family"
    assert len(r.json().get('data')[0].get('users')) == 1


def test_get_groupusers(base_url):
    """ Получение всех участников тестовой группы """
    global group_id
    global test_user_token
    r = requests.get(f'{base_url}/groups/{group_id}/', headers={"Authorization": f"Bearer {test_user_token}"})
    assert r.status_code == 200
    assert len(r.json().get('data')) == 1


def test_delete_group_user(base_url):
    """ Удаление участника из группы """
    global group_id
    global test_user_token
    global group_user_id
    r = requests.delete(f'{base_url}/groups/{group_id}/users/{group_user_id}/', headers={"Authorization": f"Bearer {test_user_token}"})
    assert r.status_code == 204


def test_delete_group(base_url):
    """ Удаление тестовой группы """
    global group_id
    global test_user_token
    r = requests.delete(f'{base_url}/groups/{group_id}/', headers={"Authorization": f"Bearer {test_user_token}"})
    assert r.status_code == 204


def test_create_event(base_url):
    """ Создание тестового события """
    global event_id
    global test_user_token
    today = str(date.today())
    payload = {"event_data": {
        "title": "New test",
        "location": "Moscow",
        "start_date": today,
        "end_date": today,
        "start_time": "14:00:00",
        "end_time": "16:00:00"
    }}
    r = requests.post(f'{base_url}/events/', headers={"Authorization": f"Bearer {test_user_token}"}, json=payload)
    event_id = r.json().get('data').get('event_data').get('id')
    assert r.status_code == 201


def test_get_event(base_url):
    """ Получение данных тестового события """
    global event_id
    global test_user_token
    r = requests.get(f'{base_url}/events/{event_id}/', headers={"Authorization": f"Bearer {test_user_token}"})
    assert r.status_code == 200


def test_patch_event(base_url):
    """ Редактирование данных тестового события """
    global event_id
    global test_user_token
    tomorrow = str(date.today() + timedelta(days=1))
    payload = {"event_data": {
        "title": "Updated test",
        "location": "New_Vasyuki",
        "end_date": tomorrow
    }}
    r = requests.patch(f'{base_url}/events/{event_id}/', headers={"Authorization": f"Bearer {test_user_token}"}, json=payload)
    assert r.status_code == 200


def test_get_events(base_url):
    """ Получение всех событий тестового пользователя на сегодня-завтра """
    global event_id
    global test_user_token
    start_date = str(date.today())
    end_date = str(date.today() + timedelta(days=1))
    r = requests.get(f'{base_url}/events/?start_date={start_date}&end_date={end_date}', headers={"Authorization": f"Bearer {test_user_token}"})
    assert r.status_code == 200
    assert len(r.json().get('data')) == 1


def test_delete_event(base_url):
    """ Удаление тестового события """
    global event_id
    global test_user_token
    r = requests.delete(f'{base_url}/events/{event_id}/', headers={"Authorization": f"Bearer {test_user_token}"})
    assert r.status_code == 204


def test_delete_user(base_url):
    """ Удаление тестового пользователя """
    global test_user_id
    global test_user_token
    r = requests.delete(f'{base_url}/users/{test_user_id}/', headers={"Authorization": f"Bearer {test_user_token}"})
    assert r.status_code == 204