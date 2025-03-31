## Yatube API

REST API для социальной сети Yatube

## Возможности

- JWT-аутентификация
- Создание/редактирование постов
- Комментирование постов
- Подписка на авторов
- Группы постов (сообщества)
- Пагинация

## Технологический стек

- Python 3.9
- Django 3.2
- Django REST Framework 3.12
- SQLite3

## Запуск проекта

``git clone https://github.com/DenixSaw/api_final_yatube`` - клонирование репозитория из github

``python3 -m venv .venv`` - создание виртуальной среды

``source .venv/bin/activate`` - активация виртуальной среды

``pip install -r requirements.txt`` - установка зависимостей

``cd /yatube_api`` - переход в главную директорию проекта

``python3 manage.py migrate`` - совершение миграций

``python3 manage.py runserver <номер порта (опционально)>`` - запуск приложения (REST-API)

