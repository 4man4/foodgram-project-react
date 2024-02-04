# Проект «Foodgram»

[![Main Foodgram Workflow](https://github.com/4man4/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/4man4/foodgram_project_react/actions/workflows/main.yml)

## Описание
Кулинарная социальная сеть &#127858;<br>
[http://4man4.ddns.net](http://4man4.ddns.net)<br>
Проект также доступен по IP-адресу: [http://158.160.20.128](http://158.160.20.128)

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
- React


## Подготовка и запуск проекта с DockerHub

Для запуска проекта необходимо создать каталог `foodgram` и перейти в него:
```shell
mkdir foodgram && cd foodgram
```

Скопировать файл `docker-compose.production.yml` в каталог проекта `foodgram`.

Сборка и запуск проекта:
```shell
sudo docker compose -f docker-compose.production.yml up
```


## Клонирование и запуск проекта с GitHub

Клонировать репозиторий:
```shell
git clone git@github.com:4man4/foodgram-project-react.git
```

Необходимо скопировать файлы `docker-compose.yml` и `.env` в каталог проекта на сервер.
После первого коммита в ветку `master` произойдет автоматический деплой проекта.

После деплоя подключиться к серверу по протоколу SSH, перейти в каталог проекта и выполнить следующие команды:

#### Войти в контейнер `backend`
```shell
sudo docker exec -it backend bash
```

#### Выполнить подготовку БД:
```shell
python manage.py migrate
```

#### Выполнить подготовку статики:
```shell
python manage.py collectstatic
```

#### Импортировать ингредиенты и теги в БД:
```shell
python manage.py import_data
```

#### Подготовить информацию для создания администратора, заменив значения в кавычках на свои:
```shell
echo -e "DJANGO_SUPERUSER_USERNAME='username'\nDJANGO_SUPERUSER_PASSWORD='password'\nDJANGO_SUPERUSER_FIRSTNAME='firstname'\nDJANGO_SUPERUSER_LASTNAME='lastname'\nDJANGO_SUPERUSER_EMAIL='email@gmail.com'\n" > .env
```

#### Загрузить переменные среды:
```shell
source .env
```

#### Создать администратора:
```shell
python manage.py createsuperuser --username $DJANGO_SUPERUSER_USERNAME --first_name $DJANGO_SUPERUSER_FIRSTNAME --last_name $DJANGO_SUPERUSER_LASTNAME --email $DJANGO_SUPERUSER_EMAIL --noinput
```

После выполнения команд проект будет доступен по вашему адресу.

Пример готового проекта:<br>
[http://4man4.ddns.net/](http://4man4.ddns.net/)


## Индивидуальные переменные и настройки

Скопировать шаблон `.env.example` с индивидуальными переменными окружения и заполнить их:

&#35; Backend settings<br>
_SECRET_KEY_ - токен Django-приложения<br>
_DEBUG_ - активация режима отладки (по умолчанию - False)<br>
_ALLOWED_HOSTS_ - разрешенные IP-адреса и доменные имена<br>
_LANGUAGE_CODE_ - язык проекта<br>
_TIME_ZONE_ - часовой пояс<br>

&#35; Database settings<br>
_DB_ENGINE_ - используемая в проекте БД<br>
_POSTGRES_DB_ - имя БД<br>
_POSTGRES_USER_ - имя пользователя БД<br>
_POSTGRES_PASSWORD_ - пароль пользователя БД <br>
_POSTGRES_HOST_ - имя контейнера с БД<br>
_POSTGRES_PORT_ - порт для подключения к БД<br>

&#35; Superuser settings<br>
_DJANGO_SUPERUSER_USERNAME_ - имя пользователя администратора<br>
_DJANGO_SUPERUSER_PASSWORD_ - пароль<br>
_DJANGO_SUPERUSER_FIRSTNAME_ - имя<br>
_DJANGO_SUPERUSER_LASTNAME_ - фамилия<br>
_DJANGO_SUPERUSER_EMAIL_ - электронная почта<br>


## Автор

**Петр Горюнов**  
[Профиль GitHub](https://github.com/4man4)