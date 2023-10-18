# Проект «Kittygram»

[![Main Foodgram Workflow](https://github.com/4man4/foodgram_project/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/4man4/foodgram_project/actions/workflows/main.yml)

## Описание
Кулинарная социальная сеть &#127858;<br>
[https://4man4.ddns.net](https://4man4.ddns.net)

Позволяет публиковать рецепты своих любимых блюд, добавлять в избранное чужие и получать список покупок для их приготовления.

Для просмотра рецептов регистрация не обязательна. Публикации собственных рецептов необходима регистрация.
Возможно редактировать только самостоятельно опубликованные рецепты. 

### Используемые технологии
- Python 3.9.10
- Django 3.2.20
- Django REST Framework
- Gunicorn
- Docker
- HTML
- CSS
- JavaScript


## Подготовка и запуск проекта с DockerHub

Для запуска проекта необходимо создать каталог `foodgram` и перейти в него:
```bash
mkdir foodgram && cd foodgram
```

Скопировать файл `docker-compose.production.yml` в каталог проекта `foodgram`.

Сборка и запуск проекта:
```bash
sudo docker compose -f docker-compose.production.yml up
```


## Клонирование и запуск проекта с GitHub

Клонировать репозиторий:
```bash
git clone git@github.com:4man4/foodgram-project-react.git
```

Перейти в каталог проекта и выполнить сборку и запуск проекта:
```bash
cd foodgram && sudo docker compose -f docker-compose.yml up
```

Выполнить подготовку БД:
```bash
sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
```

Выполнить подготовку статики:
```bash
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic
```
```bash
sudo docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /static/
```

После выполнения команд проект будет доступен по адресу:<br>
[https://localhost:9000/](https://localhost:9000/)

Остановить проект можно двумя способами:
- Нажать `Ctrl` + `C` в терминале, откуда был выполнен запуск
- Выполнить команду в новом терминале
```bash
sudo docker compose -f docker-compose.yml down
```


## Индивидуальные переменные и настройки

Скопировать шаблон с индивидуальными переменными окружения:
```bash
sudo cp .env.example .env
```

_POSTGRES_DB_ - имя БД
_POSTGRES_USER_ - имя пользователя БД
_POSTGRES_PASSWORD_ - пароль пользователя БД 
_DB_NAME_ - имя образа БД
_DB_HOST_ - имя машины с БД 
_DB_PORT_ - порт для подключения к БД
_SECRET_KEY_ - токен Django-приложения  
_DEBUG_ - активация режима отладки (по умолчанию - False)  
_ALLOWED_HOSTS_ - разрешенные IP-адреса и доменные имена  


## Автор

**Петр Горюнов**  
[Профиль GitHub](https://github.com/4man4)