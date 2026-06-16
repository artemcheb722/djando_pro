DC = docker compose

.PHONY: build up down shell migrate restart makemigrations

build:
	${DC} build

up:
	${DC} up

down:
	${DC} down

shell:
	${DC} exec web python manage.py shell

migrate:
	${DC} exec web python manage.py migrate

makemigrations:
	${DC} exec web python manage.py makemigrations

createsuperuser:
	${DC} exec web python manage.py createsuperuser

restart:
	${DC} down && ${DC} up -d


