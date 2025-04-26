# API для мобильного приложения "Family Planner" 

<details>
<summary>

## Описание

</summary>

***Мобильное приложение "Family Planner" позволяет создавать календари, различные списки (todo списки, списки покупок и др.), планировать события, в том числе
регулярные. Основная фишка - возможность совместного использования членами семьи (или группы), делегирование задач.***

</details>

___

<details>
<summary>

## Технологии

</summary>

### Backend
*Django Rest Framework, Swagger*

### Tools


### Containerization
*Docker, Docker Compos, Nginx*


### QA
*Postman, PyTest*

</details>

___

<details>
<summary>

## Как запустить проект на своем локальном сервере через IDE PyCharm

</summary>

### 1. Клонирование репозитория

```
git clone https://git.infra.cloveri.com/cloveri.start/step/step_latest.git
```

### 2. Создание виртуального окружения

```
python -m venv venv - для Windows
sudo apt-get install -y python3-venv - для Linux
```

### 3. Активирование виртуального окружение

```
venv\scripts\activate  - для Windows
venv/bin/activate - для Linux
```

### 4. Установка переменных окружения

***В корне проекта заполняем файл .env.example и переименовываем его в .env или просто создаём файл .env и
заполняем его.***

```
SECRET_KEY='mysecretkey78849'
DEBUG=1

DJANGO_ALLOWED_HOSTS=api.step.skroy.ru 127.0.0.1
DJANGO_CORS_ALLOWED_ORIGINS=http://127.0.0.1:3000 https://step.skroy.ru

BASE_URL=https://api.beta.raida-dev.ru
USER_RAIDA=raida@raida.com
PASSWD_RAIDA=raida

STEP_SERVICE_MAIN_PORT=8001
STEP_SERVICE_MAIN_IMAGE=docker.infra.cloveri.com/cloveri.start/step/step/stage:latest

LANGUAGE_CODE=ru
TIME_ZONE=Europe/Moscow

```

### 5. Установка зависимостей

```
pip install -r requirements.txt
```

### 6. Запуск сервиса

```
python manage.py runserver
```

</details>

___

<details>
<summary>

## Команда Кловери Шаг 9 поток

</summary>

| № | ФИО                | Должность           | Никнейм в телеграмме | Ссылка на проекты               |
|---|--------------------|---------------------|----------------------|---------------------------------|
| 1 | Филипенко Виктория | Заказчик, дизайнер  | @up2fika             |                                 |
| 2 | Зайцев Антон       | Backend разработчик | @BlackMarvel         | https://github.com/Hashtagich   |
| 3 | Алехина Ольга      | Backend разработчик | @olik_al             | https://github.com/OlgaAlekhina |
| 4 | Спащенко Регина    | QA                  | @Sp_R_G              | https://github.com/SpaRegina    |

</details>

___

## Urls и API

***Страница с документацией по API***

<code>/docs/</code>

***API Конфигураций***

<details>
<summary><code>GET/configs/</code></summary>

*Получение всех идентификаторов из реестра*

```
{
  "data": "string"
}
```

</details>

<details>
<summary><code>GET/configs/{config_type}/</code></summary>

*Получение идентификаторов типа {config_type} из реестра*

```
{
  "data": "string"
}
```

</details>

<details>
<summary><code>POST/configs/</code></summary>

*Добавление идентификаторов в реестр*

```
{
  "project_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "object_type": "string",
  "data": "string"
}
```

</details>

***API для вкладок/разделов личного кабинета Кловери Шаг (Конкурсы)***
<details>
<summary><code>GET/contests/{contest_id}/</code></summary>

*Получение данных конкретного конкурса по его id*

```
{
  "detail": {
    "code": "string",
    "message": "string"
  },
  "data": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "title": "string",
    "description": "string",
    "created_at": "2024-12-04",
    "status_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "status_name": "string",
    "deadline": "2024-12-04",
    "award": "string",
    "profession": "string",
    "category": "string",
    "attachments": {
      "id": "string",
      "name": "string"
    }
  },
  "info": {
    "api_version": "string",
    "count": 0
  }
}
```

</details>

<details>
<summary><code>GET/contests/active/</code></summary>

*Получение списка всех конкурсов со статусом Прием работ. Вкладка/раздел Активные конкурсы.*

```
{
  "detail": {
    "code": "string",
    "message": "string"
  },
  "data": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "description": "string",
      "status": "string",
      "deadline": "2024-12-05",
      "award": "string",
      "brief": "string",
      "title": "string",
      "konkurs_category": "string"
    }
  ],
  "info": {
    "api_version": "string",
    "count": 0
  }
}
```

</details>


<details>
<summary><code>GET/contests/archive/</code></summary>

*Получение списка всех конкурсов со статусом Завершен и Победитель не выбран. Вкладка/раздел Архив конкурсов.*

```
{
  "detail": {
    "code": "string",
    "message": "string"
  },
  "data": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "description": "string",
      "status": "string",
      "deadline": "2024-12-05",
      "award": "string",
      "brief": "string",
      "title": "string",
      "konkurs_category": "string"
    }
  ],
  "info": {
    "api_version": "string",
    "count": 0
  }
}
```

</details>


<details>
<summary><code>GET/contests/user/my/history/</code></summary>

*Получение списка всех завершенных конкурсов, где пользователя участвовал. Вкладка/раздел История участия.*

```
{
  "detail": {
    "code": "OK",
    "message": "Получение списка всех конкурсов со статусом Завершен. Для раздела история участия."
  },
  "data": [
    {
      "id": "e2ccc043-2558-4bd1-872e-4df6cf7b5256",
      "title": "Супер-конкурс",
      "created_at": "06 November 2024",
      "deadline": "28 November 2024",
      "solution_link": "test_link",
      "attachments": {
        "id": "ce063f59-e352-4da9-939f-253644619eb4",
        "name": "f6e3f9a9-79ea-4859-82ea-b1721bff0c70-cat.jpg",
        "url": "media/4fc9986b-d03b-4801-a672-a191c941e17c/f6e3f9a9-79ea-4859-82ea-b1721bff0c70-cat.jpg",
        "content_type": "image/jpeg"
      }
    }
  ],
  "info": {
    "api_version": "0.0.1",
    "count": 1
  }
}
```

</details>

<details>
<summary><code>GET/contests/user/{user_id}/history/</code></summary>

*Получение списка всех завершенных конкурсов конкретного участника, где тот участвовал.*

```
{
  "detail": {
    "code": "OK",
    "message": "Получение списка всех конкурсов со статусом Завершен. Для раздела история участия."
  },
  "data": [
    {
      "id": "e2ccc043-2558-4bd1-872e-4df6cf7b5256",
      "title": "Супер-конкурс",
      "created_at": "06 November 2024",
      "deadline": "28 November 2024",
      "solution_link": "test_link",
      "attachments": {
        "id": "ce063f59-e352-4da9-939f-253644619eb4",
        "name": "f6e3f9a9-79ea-4859-82ea-b1721bff0c70-cat.jpg",
        "url": "media/4fc9986b-d03b-4801-a672-a191c941e17c/f6e3f9a9-79ea-4859-82ea-b1721bff0c70-cat.jpg",
        "content_type": "image/jpeg"
      }
    }
  ],
  "info": {
    "api_version": "0.0.1",
    "count": 1
  }
}
```

</details>


<details>
<summary><code>GET/contests/user/my/tasks/</code></summary>

*Получение списка всех заданий пользователя. Вкладка/раздел Мои задания.*

```
{
  "detail": {
    "code": "string",
    "message": "string"
  },
  "data": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "title": "string",
      "description": "string",
      "status_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "status_name": "string",
      "deadline": "2024-12-11",
      "award": "string",
      "brief": "string",
      "profession": "string",
      "projects": "string",
      "konkurs_category": "string",
      "application_status": {
        "application_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "application_status": {
          "code": "string",
          "message": "string"
        },
        "solution_link": "string"
      }
    }
  ],
  "info": {
    "api_version": "string",
    "count": 0
  }
}
```

</details>

<details>
<summary><code>POST/contests/user/my/task/</code></summary>

*Создание задачи для участия в конкурсе*

```
{
  "detail": {
    "code": "string",
    "message": "string"
  },
  "data": {
    "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "status": "string",
    "contest_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  },
  "info": {
    "api_version": "string",
    "count": 0
  }
}
```

</details>

<details>
<summary><code>DELETE/contests/user/my/task/{task_id}/</code></summary>

*Отказ от участия в конкурсе: изменение статуса заявки на 'Отказ'*

```
{
  "detail": {
    "code": "string",
    "message": "string"
  },
  "info": {
    "api_version": "string",
    "count": 0
  }
}
```

</details>

<details>
<summary><code>GET/contests/{contest_id}/task/</code></summary>

*Получение списка задач/участий в конкурсах по переданным статусам/у в рамках конкретного конкурса<br>
Пример запроса по одному статусу {url}/contests/{contest_id}/task/?status={status_id1}<br>
Пример запроса по двум статусам {url}/contests/{contest_id}/task/?status={status_id1}&status={status_id2}*

```
{
  "detail": {
    "code": "string",
    "message": "string"
  },
  "data": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "title": "string",
      "description": "string",
      "status_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "status_name": "string",
      "deadline": "2024-12-11",
      "award": "string",
      "brief": "string",
      "projects": "string",
      "konkurs_category": "string"
    }
  ],
  "info": {
    "api_version": "string",
    "count": 0
  }
}
```

</details>

___

<details>
<summary>

## Дополнительная информация

</summary>

+ ***Дизайн в Figma — https://www.figma.com/design/3r9HwWIEHWElYElRLtc8Gq/ЛК-Кловери.Шаг?node-id=0-1***
+ ***Документация по стажировке 9 потока — https://drive.google.com/drive/folders/1xQej-LEGexAl7P4fzTCJnw2Gl4MeS1T-***

</details>