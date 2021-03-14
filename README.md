# Проект Yatube 
Yatube – это социальная сеть для публикации статей с группами, подпиской на авторов, лентой избранных авторов. \
Использованный стек: Python, Django, SQLite, Django ORM. Для проекта написаны unittest’ы. Проект прошел код ревью. \
Проект запущен на сервере Яндекс.Облако, настроен NGINX, WSGI Gunicorn, https, база данных перенесена с SQLite на PostgreSQL.\
Для мониторинга доступности и сбора ошибок подключены UptimeRobot и Sentry

## Установка
Клонировать репозиторий

    $ git clone https://github.com/Ilia-Abrosimov/hw05_final

Создание виртуального окружения

    $ python -m venv venv
  
Запуск виртуального окружения в Windows

    $ source venv/Scripts/activate
    или в macOS/Linux
    $ source venv/bin/activate 
   
Установка зависимостей

    $ pip install -r requirements.txt 

Применение миграций БД

    $ python manage.py migrate

Запуск

    $ python manage.py runserver
