COMPOSE = sudo docker compose -f docker-compose.yml

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f django

bash:
	$(COMPOSE) exec django bash

migrate:
	$(COMPOSE) exec django python manage.py migrate

makemigrations:
	$(COMPOSE) exec django python manage.py makemigrations

createsuperuser:
	$(COMPOSE) exec django python manage.py createsuperuser

pyshell:
	$(COMPOSE) exec django python manage.py shell

runserver:
	python3 app/manage.py runserver
