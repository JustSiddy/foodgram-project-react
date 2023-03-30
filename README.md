# Проект FoodGram 

![Foodgram workflow](https://github.com/justsiddy/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Описание проекта.
В этом проекте представлен сайт, в котором можно публиковать рецепты разных блюд. 
Так же пользователи могут:
- подписываться на публикации других пользователей
- добавлять понравившиеся рецепты в сприсок "Избранное"
- могут скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд

## Технологии
```
Python
Django
Django Rest Framework
Docker
PostgresSQL
Nginx
Gunicorn
YandexCloud
```

### Проект доступен по адресу: http://158.160.3.114/signin

## Настрока и запуск сервера в контейнере:
1) Клонировать репозиторий:
``` 
git clone https://github.com/JustSiddy/foodgram-project-react.git
```
2) Переидти в папку:
``` 
cd infra
```
3) Создать файл .env и заполнить ее переменными окружения, для стабильной работы приложения. 
Пример содержимого файла:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
4) Развернуть контейнер:
``` 
docker-compose up -d --build
```
5) Сделать миграции, создать суперпользователя, собрать статику
``` 
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```
6) Загрузить базу данных из копии:
``` 
sudo docker-compose exec backend python manage.py loaddata ingredients.json
```

## Автор
- [Расули Саид](https://github.com/JustSiddy)

